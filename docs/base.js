document.addEventListener('keyup', (e) => {
    if (e.ctrlKey && e.key == 'i') {
        document.querySelector('#ir').focus();
    }
});

document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('#mostrar_versoes').addEventListener('change', () => {
        const obsoletos = document.querySelectorAll('.obsoleta');

        if (obsoletos.length > 0) {
            obsoletos.forEach(item => {
                item.classList.toggle('is-hidden');
            });
        }
    });

    document.querySelector('#ir').addEventListener('keyup', (e) => {
        if (e.code == 'Enter') {
            const destino = document.querySelector('#a' + e.currentTarget.value);

            if (destino === null) {
                window.alert('O artigo não foi encontrado.');
                e.currentTarget.focus();
            } else {
                destino.scrollIntoView({ behavior: 'smooth' });
                e.currentTarget.value = '';
            }
        }
    });

    const instrumentos = document.querySelectorAll('span[data-instrumento]');

    if (instrumentos.length > 0) {
        instrumentos.forEach(el => {
            const span = document.createElement('span');
            span.className = 'tag is-light ml-2';
            span.appendChild(document.createTextNode(el.attributes['data-instrumento'].value));

            const alvo = el;

            if (el.firstElementChild !== null && el.firstElementChild.tagName === 'DEL') {
                alvo = el.firstElementChild;
            }

            alvo.appendChild(span);
        });
    }
});