import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';

/** Adaptador para MapLibre 5.24.0. Solo vista local Mercator.
 * Los puntos y la densidad los aporta la aplicación, no este módulo. */
export class SmartSeedsPlants3D {
  constructor(map, {maplibre=globalThis.maplibregl, spriteLayer='plantas', id='smartseeds-plantas-3d', escalaVisual=1, baseURL=new URL('./',import.meta.url)}={}) {
    this.map=map; this.lib=maplibre; this.spriteLayer=spriteLayer; this.id=id;
    this.scale=escalaVisual; this.baseURL=baseURL; this.loader=new GLTFLoader();
    this.token=0; this.visible=true; this.ready=false; this.meshes=[];
    this.camera=new THREE.Camera(); this.scene=new THREE.Scene();
    this.scene.rotation.x=Math.PI/2; this.scene.scale.z=-1;
    this.scene.add(new THREE.HemisphereLight(0xffffff,0x2c3a1e,1.25));      // (SmartSeeds) luz más baja: con la de antes las plantas salían lavadas
    const sun=new THREE.DirectionalLight(0xfff0d8,2.1); sun.position.set(30,70,-40); this.scene.add(sun);
    const self=this;
    this.layer={id,type:'custom',renderingMode:'3d',onAdd(m,gl){
      self.renderer=new THREE.WebGLRenderer({canvas:m.getCanvas(),context:gl});
      self.renderer.autoClear=false;
    },render(gl,args){self.render(args)},onRemove(){self.renderer?.dispose();self.renderer=null;}};
    this.refresh=()=>{if(!this.timer)this.timer=setTimeout(()=>{this.timer=null;this.updateElevations()},120)};
    this.style=()=>{this.ready=false;this.ensureLayer();this.refresh()};
    map.on('style.load',this.style);map.on('idle',this.refresh);map.on('sourcedata',this.refresh);
    this.ensureLayer();
  }
  ensureLayer(){if(this.map.isStyleLoaded()&&!this.map.getLayer(this.id))this.map.addLayer(this.layer);}
  sprites(show){if(this.map.getLayer(this.spriteLayer))this.map.setLayoutProperty(this.spriteLayer,'visibility',show?'visible':'none');}
  setVisible(value){this.visible=!!value;this.sprites(!this.visible||!this.ready);this.map.triggerRepaint();}
  clear(){for(const m of this.meshes){this.scene.remove(m);m.dispose();}this.meshes=[];
    this.root?.traverse(o=>{if(o.isMesh){o.geometry.dispose();for(const m of Array.isArray(o.material)?o.material:[o.material])m.dispose()}});this.root=null;}
  async setCultivo(clave, geojson, {ligero, escalaVisual=this.scale}={}) {
    const token=++this.token; this.ready=false;this.sprites(true);this.clear();this.points=[];
    const features=Array.isArray(geojson)?geojson:(geojson?.features||[]);
    this.points=features.filter(f=>f.geometry?.type==='Point').map(f=>f.geometry.coordinates.slice(0,2)).filter(p=>p.every(Number.isFinite)).slice(0,260);
    if(!this.points.length){this.map.triggerRepaint();return false}
    if(!/^[a-z_]+$/.test(clave))throw new Error('Clave de cultivo inválida');
    const low=ligero??this.points.length>60;
    try {
      const gltf=await this.loader.loadAsync(new URL(`modelos/${low?'lod/':''}${clave}.glb`,this.baseURL).href);
      if(token!==this.token){gltf.scene.traverse(o=>{if(o.isMesh){o.geometry.dispose();for(const m of Array.isArray(o.material)?o.material:[o.material])m.dispose()}});return false}
      this.root=gltf.scene;this.root.updateMatrixWorld(true);this.scale=escalaVisual;
      // (SmartSeeds) más color: cada color del modelo se satura y se oscurece un poco, para que la planta
      // contraste con la foto clara del terreno. No cambia la forma.
      const tinta=new THREE.Color(),hsl={};
      this.root.traverse(o=>{if(!o.isMesh)return;const colores=o.geometry.getAttribute('color');
        if(colores&&!o.geometry.userData.intensificado){o.geometry.userData.intensificado=true;
          for(let i=0;i<colores.count;i++){tinta.setRGB(colores.getX(i),colores.getY(i),colores.getZ(i)).getHSL(hsl);
            tinta.setHSL(hsl.h,Math.min(1,hsl.s*1.55+0.08),hsl.l*0.74);colores.setXYZ(i,tinta.r,tinta.g,tinta.b);}
          colores.needsUpdate=true;}
        for(const m of Array.isArray(o.material)?o.material:[o.material]){if(!colores){m.color.getHSL(hsl);m.color.setHSL(hsl.h,Math.min(1,hsl.s*1.55+0.08),hsl.l*0.74);}
          if('roughness' in m)m.roughness=1;if('metalness' in m)m.metalness=0;}});
      this.root.traverse(o=>{if(o.isMesh){const m=new THREE.InstancedMesh(o.geometry,o.material,this.points.length);
        m.userData.sourceMatrix=o.matrixWorld.clone();m.frustumCulled=false;this.meshes.push(m);this.scene.add(m);}});
      this.ensureLayer();this.updateElevations();return true;
    } catch(error){if(token===this.token){this.ready=false;this.sprites(true);console.warn('SMARTSEEDS: se conservan los símbolos 2D.',error)}return false}
  }
  updateElevations(){
    if(!this.root||!this.points.length)return;
    // No altera el globo de portada: la app cambia explícitamente a Mercator al entrar a la parcela.
    if((this.map.getProjection()?.type??'mercator')!=='mercator'){this.ready=false;this.sprites(true);return}
    const terrain=!!this.map.getTerrain();
    const heights=this.points.map(p=>terrain?this.map.queryTerrainElevation(p):0);
    if(heights.some(h=>!Number.isFinite(h))){this.ready=false;this.sprites(true);return}
    const signature=JSON.stringify(heights);if(this.ready&&signature===this.heightSignature)return;this.heightSignature=signature;
    this.origin=this.lib.MercatorCoordinate.fromLngLat(this.points[0],heights[0]);
    const meter=this.origin.meterInMercatorCoordinateUnits();
    const object=new THREE.Object3D(),matrix=new THREE.Matrix4();
    this.points.forEach((p,i)=>{const q=this.lib.MercatorCoordinate.fromLngLat(p);
      object.position.set((q.x-this.origin.x)/meter,heights[i]-heights[0],(this.origin.y-q.y)/meter);
      object.rotation.set(0,Math.sin(i*19.17)*Math.PI,0);object.scale.setScalar(this.scale);object.updateMatrix();
      for(const m of this.meshes){matrix.multiplyMatrices(object.matrix,m.userData.sourceMatrix);m.setMatrixAt(i,matrix);}});
    for(const m of this.meshes)m.instanceMatrix.needsUpdate=true;
    // queryTerrainElevation ya incorpora la exageración del DEM; no multiplicar por 1,4.
    this.ready=true;this.sprites(!this.visible);this.map.triggerRepaint();
  }
  render(args){if(!this.visible||!this.ready||!this.renderer||!this.origin)return;
    if((this.map.getProjection()?.type??'mercator')!=='mercator')return;
    // (SmartSeeds) Three guarda el tamaño del lienzo de cuando nació; si la ventana cambió de tamaño hay que avisarle,
    // o dibuja las plantas corridas respecto del mapa.
    const lienzo=this.map.getCanvas();
    if(lienzo.width!==this.anchoVisto||lienzo.height!==this.altoVisto){this.anchoVisto=lienzo.width;this.altoVisto=lienzo.height;this.renderer.setViewport(0,0,lienzo.width,lienzo.height);}
    const p=new THREE.Matrix4().fromArray(args.defaultProjectionData.mainMatrix),s=this.origin.meterInMercatorCoordinateUnits();
    const local=new THREE.Matrix4().makeTranslation(this.origin.x,this.origin.y,this.origin.z).scale(new THREE.Vector3(s,-s,s));
    this.camera.projectionMatrix.multiplyMatrices(p,local);
    this.renderer.resetState();this.renderer.render(this.scene,this.camera);this.renderer.resetState();
  }
  dispose(){++this.token;clearTimeout(this.timer);this.map.off('style.load',this.style);this.map.off('idle',this.refresh);this.map.off('sourcedata',this.refresh);this.clear();if(this.map.getLayer(this.id))this.map.removeLayer(this.id);this.sprites(true);}
}
