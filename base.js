document.addEventListener('keyup', (e) => {
    if (e.ctrlKey && e.key == 'i') {
        document.querySelector('#ir').focus();
    }
});

document.addEventListener('DOMContentLoaded', () => {
    var obsoletos = document.querySelectorAll('.obsoleta');
    var controle_mostrar = document.querySelector('#mostrar_versoes');
    var controle_ir = document.querySelector('#ir');

    controle_mostrar.addEventListener('change', () => {
        if (obsoletos.length > 0) {
            obsoletos.forEach(item => {
                item.classList.toggle('is-hidden');
            });
        }
    });

    controle_ir.addEventListener('keyup', (e) => {
        if (e.code == 'Enter') {
            let destino = document.querySelector('#a' + e.currentTarget.value);

            if (destino === null) {
                window.alert('O artigo não foi encontrado.');
                e.currentTarget.focus();
            } else {
                destino.scrollIntoView({ behavior: 'smooth' });
                e.currentTarget.value = '';
            }
        }
    });

    var instrumentos = document.querySelectorAll('span[data-instrumento]');

    if (instrumentos.length > 0) {
        instrumentos.forEach(el => {
            var span = document.createElement('span');
            span.className = 'tag is-light ml-2';
            span.appendChild(document.createTextNode(el.attributes['data-instrumento'].value));

            var alvo = el;

            if (el.firstElementChild.tagName === 'DEL') {
                alvo = el.firstElementChild;
            }

            alvo.appendChild(span);
        });
    }
});