<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-md p-4">
    <div class="relative w-full max-w-lg bg-slate-900 border border-slate-700 rounded-xl overflow-hidden shadow-2xl flex flex-col">
      <!-- Header -->
      <div class="bg-slate-800 p-4 border-b border-slate-700 flex justify-between items-center z-10">
        <h3 class="text-slate-100 font-bold flex items-center">
          <span class="mr-2 text-neoYellow">🎯</span> Vision Preprocessing
        </h3>
        <button @click="$emit('cancel')" class="text-slate-400 hover:text-white transition-colors">
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
        </button>
      </div>

      <!-- Canvas Area -->
      <div 
        ref="containerRef"
        class="relative w-full h-[60vh] bg-black flex items-center justify-center overflow-hidden touch-none"
      >
        <canvas 
          ref="canvasRef" 
          class="absolute touch-none cursor-crosshair"
          style="touch-action: none;"
          @mousedown="handlePointerDown"
          @mousemove="handlePointerMove"
          @mouseup="handlePointerUp"
          @mouseleave="handlePointerUp"
          @touchstart.prevent="handlePointerDown"
          @touchmove.prevent="handlePointerMove"
          @touchend.prevent="handlePointerUp"
        ></canvas>
      </div>

      <!-- Footer Controls -->
      <div class="bg-slate-800 p-4 border-t border-slate-700 flex gap-3 z-10">
        <button 
           @click="$emit('cancel')" 
           class="flex-1 py-2.5 bg-slate-700 hover:bg-slate-600 text-slate-300 font-medium rounded-lg transition-colors border border-slate-600"
        >
          Cancel
        </button>
        <button 
           @click="autoAccept" 
           class="flex-1 py-2.5 bg-neoBlue/20 hover:bg-neoBlue/40 text-neoBlue font-medium rounded-lg transition-colors border border-neoBlue/30"
           title="90% Center Crop"
        >
          Auto 90%
        </button>
        <button 
           @click="exportCrop" 
           class="flex-1 py-2.5 bg-neoYellow hover:bg-yellow-500 text-slate-900 font-bold rounded-lg transition-all shadow-[0_0_15px_rgba(234,179,8,0.3)]"
        >
          Scan
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

const props = defineProps({
  imageUrl: { type: String, required: true }
})
const emit = defineEmits(['crop', 'cancel'])

const containerRef = ref(null)
const canvasRef = ref(null)

let ctx = null
let img = null
let canvasScale = 1

// Crop box constraints in canvas coordinates
let cropBox = { x: 0, y: 0, w: 0, h: 0 }
let isDragging = false
let dragAction = null // 'move', 'nw', 'ne', 'sw', 'se'
let dragStart = { x: 0, y: 0 }
let initialCropBox = null

onMounted(async () => {
  await nextTick()
  initCanvas()
})

const initCanvas = () => {
  const canvas = canvasRef.value
  const container = containerRef.value
  if (!canvas || !container) return
  
  ctx = canvas.getContext('2d', { willReadFrequently: true })
  
  img = new Image()
  img.onload = () => {
    // Fit canvas visually inside container while maintaining resolution
    const containerW = container.clientWidth
    const containerH = container.clientHeight
    
    const scale = Math.min(containerW / img.width, containerH / img.height)
    canvasScale = scale
    
    // Virtual resolution (display css size)
    canvas.style.width = `${img.width * scale}px`
    canvas.style.height = `${img.height * scale}px`
    
    // Internal canvas resolution
    canvas.width = img.width
    canvas.height = img.height
    
    // Init default 90% crop box
    resetCropBox()
    draw()
  }
  img.src = props.imageUrl
}

const resetCropBox = () => {
  const paddingX = img.width * 0.05
  const paddingY = img.height * 0.05
  cropBox = {
    x: paddingX,
    y: paddingY,
    w: img.width * 0.9,
    h: img.height * 0.9
  }
}

const draw = () => {
  if (!ctx || !img) return
  
  ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
  
  // Draw base image
  ctx.drawImage(img, 0, 0)
  
  // Draw semi-transparent dark overlay over everything
  ctx.fillStyle = 'rgba(0, 0, 0, 0.6)'
  ctx.fillRect(0, 0, canvasRef.value.width, canvasRef.value.height)
  
  // Cut out the crop box
  ctx.save()
  ctx.globalCompositeOperation = 'destination-out'
  ctx.fillRect(cropBox.x, cropBox.y, cropBox.w, cropBox.h)
  ctx.restore()
  
  // Draw stroke around crop box
  ctx.strokeStyle = '#10b981' // emerald-500
  ctx.lineWidth = 3 / canvasScale
  ctx.strokeRect(cropBox.x, cropBox.y, cropBox.w, cropBox.h)
  
  // Draw corner handles
  const handleSize = 25 / canvasScale
  ctx.fillStyle = '#10b981'
  const drawHandle = (x, y) => ctx.fillRect(x - handleSize/2, y - handleSize/2, handleSize, handleSize)
  
  drawHandle(cropBox.x, cropBox.y)
  drawHandle(cropBox.x + cropBox.w, cropBox.y)
  drawHandle(cropBox.x, cropBox.y + cropBox.h)
  drawHandle(cropBox.x + cropBox.w, cropBox.y + cropBox.h)
}

const getPointerPos = (e) => {
  const el = canvasRef.value
  const rect = el.getBoundingClientRect()
  const clientX = e.touches ? e.touches[0].clientX : e.clientX
  const clientY = e.touches ? e.touches[0].clientY : e.clientY
  return {
    x: (clientX - rect.left) / canvasScale,
    y: (clientY - rect.top) / canvasScale
  }
}

const handlePointerDown = (e) => {
  const pos = getPointerPos(e)
  isDragging = true
  dragStart = pos
  initialCropBox = { ...cropBox }
  
  const thresh = 40 / canvasScale
  // Determine if grab is corner or center
  if (Math.abs(pos.x - cropBox.x) < thresh && Math.abs(pos.y - cropBox.y) < thresh) dragAction = 'nw'
  else if (Math.abs(pos.x - (cropBox.x + cropBox.w)) < thresh && Math.abs(pos.y - cropBox.y) < thresh) dragAction = 'ne'
  else if (Math.abs(pos.x - cropBox.x) < thresh && Math.abs(pos.y - (cropBox.y + cropBox.h)) < thresh) dragAction = 'sw'
  else if (Math.abs(pos.x - (cropBox.x + cropBox.w)) < thresh && Math.abs(pos.y - (cropBox.y + cropBox.h)) < thresh) dragAction = 'se'
  else dragAction = 'move'
}

const handlePointerMove = (e) => {
  if (!isDragging) return
  const pos = getPointerPos(e)
  const dx = pos.x - dragStart.x
  const dy = pos.y - dragStart.y
  
  const cw = canvasRef.value.width
  const ch = canvasRef.value.height
  
  if (dragAction === 'move') {
    let nx = initialCropBox.x + dx
    let ny = initialCropBox.y + dy
    // Bounds
    nx = Math.max(0, Math.min(nx, cw - cropBox.w))
    ny = Math.max(0, Math.min(ny, ch - cropBox.h))
    cropBox.x = nx
    cropBox.y = ny
  } else {
    // Resizing logic (keeping bounds intact)
    if (dragAction === 'nw') {
      cropBox.x = Math.max(0, initialCropBox.x + dx)
      cropBox.y = Math.max(0, initialCropBox.y + dy)
      cropBox.w = initialCropBox.w - (cropBox.x - initialCropBox.x)
      cropBox.h = initialCropBox.h - (cropBox.y - initialCropBox.y)
    } else if (dragAction === 'ne') {
      cropBox.y = Math.max(0, initialCropBox.y + dy)
      cropBox.w = Math.max(10, Math.min(cw - initialCropBox.x, initialCropBox.w + dx))
      cropBox.h = initialCropBox.h - (cropBox.y - initialCropBox.y)
    } else if (dragAction === 'sw') {
      cropBox.x = Math.max(0, initialCropBox.x + dx)
      cropBox.w = initialCropBox.w - (cropBox.x - initialCropBox.x)
      cropBox.h = Math.max(10, Math.min(ch - initialCropBox.y, initialCropBox.h + dy))
    } else if (dragAction === 'se') {
      cropBox.w = Math.max(10, Math.min(cw - initialCropBox.x, initialCropBox.w + dx))
      cropBox.h = Math.max(10, Math.min(ch - initialCropBox.y, initialCropBox.h + dy))
    }
  }
  
  draw()
}

const handlePointerUp = () => {
  isDragging = false
  dragAction = null
}

const autoAccept = () => {
  resetCropBox()
  draw()
  exportCrop()
}

const exportCrop = () => {
  if (!img) return
  
  // Offscreen canvas for export
  const offCanvas = document.createElement('canvas')
  offCanvas.width = cropBox.w
  offCanvas.height = cropBox.h
  const offCtx = offCanvas.getContext('2d')
  
  // Draw only the cropped portion
  offCtx.drawImage(
    img,
    cropBox.x, cropBox.y, cropBox.w, cropBox.h,
    0, 0, cropBox.w, cropBox.h
  )
  
  // Pixel manipulating for high contrast & grayscale
  const imgData = offCtx.getImageData(0, 0, cropBox.w, cropBox.h)
  const data = imgData.data
  const contrast = 1.5
  const intercept = 128 * (1 - contrast)
  
  for (let i = 0; i < data.length; i += 4) {
    // Grayscale
    const avg = data[i] * 0.299 + data[i+1] * 0.587 + data[i+2] * 0.114
    
    // Contrast applying to grayscale
    const cVal = avg * contrast + intercept
    // clamp
    const finalVal = Math.max(0, Math.min(255, cVal))
    
    data[i] = finalVal
    data[i+1] = finalVal
    data[i+2] = finalVal
    // Alpha channel unchanged
  }
  
  offCtx.putImageData(imgData, 0, 0)
  
  offCanvas.toBlob((blob) => {
    emit('crop', blob)
  }, 'image/jpeg', 0.9)
}
</script>
