
// utils.js - Funciones de utilidad pura

export function formatearTamano(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const items = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + items[i];
}

export function parseTamano(str) {
    if (!str) return 0;
    const parts = str.trim().split(' ');
    if (parts.length < 2) return 0;
    let val = parseFloat(parts[0].replace(',', '.'));
    const unit = parts[1].toUpperCase();
    const k = 1024;
    if (unit.startsWith('KB')) val *= k;
    else if (unit.startsWith('MB')) val *= k*k;
    else if (unit.startsWith('GB')) val *= k*k*k;
    return val;
}

export function obtenerConfiguracionIcono(file) {
    const n = file.name.toLowerCase();
    if (n.endsWith('.pdf')) return { clase: 'icon-pdf', svg: '<span class="material-symbols-outlined">picture_as_pdf</span>' };
    if (/\.(jpg|jpeg|png)$/.test(n)) return { clase: 'icon-img', svg: '<span class="material-symbols-outlined">image</span>' };
    return { clase: 'icon-fig', svg: '<span class="material-symbols-outlined">draft</span>' };
}

export function detectarTipo(nombre) {
    if (!nombre) return 'otro';
    const n = nombre.toLowerCase();
    
    // PDF
    if (n.endsWith('.pdf')) return 'pdf';
    
    // Imágenes
    if (/\.(jpg|jpeg|png|gif|webp|svg|bmp|ico)$/.test(n)) return 'imagen';
    
    // Videos
    if (/\.(mp4|mov|avi|webm|mkv|flv|wmv)$/.test(n)) return 'video';
    
    // Audio
    if (/\.(mp3|wav|ogg|m4a|flac|aac)$/.test(n)) return 'audio';
    
    // Documentos
    if (/\.(doc|docx|txt|rtf|odt)$/.test(n)) return 'documento';
    
    // Hojas de cálculo
    if (/\.(xls|xlsx|csv|ods)$/.test(n)) return 'hoja_calculo';
    
    // Presentaciones
    if (/\.(ppt|pptx|odp)$/.test(n)) return 'presentacion';
    
    // Archivos comprimidos
    if (/\.(zip|rar|7z|tar|gz|bz2)$/.test(n)) return 'archivo';
    
    // Código
    if (/\.(html|css|js|jsx|ts|tsx|py|java|c|cpp|php|rb|go|rs)$/.test(n)) return 'codigo';
    
    return 'otro';
}
