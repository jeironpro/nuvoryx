import { inicializarInterfaz } from './modules/interfaz.js';
import { inicializarSubidas } from './modules/subidas.js';
import { inicializarArchivos } from './modules/archivos.js';
import { inicializarAutenticacion } from './modules/autenticacion.js';
import { inicializarFiltros } from './modules/filtros.js';

document.addEventListener('DOMContentLoaded', () => {
    inicializarInterfaz();
    inicializarSubidas();
    inicializarArchivos();
    inicializarAutenticacion();
    inicializarFiltros();
});
