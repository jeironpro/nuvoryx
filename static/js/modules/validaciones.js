export const validaciones = {
    validarContrasena: (password) => {
        let fuerza = 0;
        const mensajes = [];

        if (password.length >= 8) fuerza += 20;
        else mensajes.push("Mínimo 8 caracteres");

        if (password.match(/[A-Z]/)) fuerza += 20;
        else mensajes.push("Al menos una mayúscula");

        if (password.match(/[a-z]/)) fuerza += 20;
        else mensajes.push("Al menos una minúscula");

        if (password.match(/[0-9]/)) fuerza += 20;
        else mensajes.push("Al menos un número");

        if (password.match(/[^A-Za-z0-9]/)) fuerza += 20;
        else mensajes.push("Al menos un símbolo");

        return {
            valido: fuerza === 100,
            fuerza: fuerza,
            mensajes: mensajes
        };
    },

    validarEmail: (email) => {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    validarCoincidencia: (pass1, pass2) => {
        return pass1 === pass2 && pass1.length > 0;
    }
};
