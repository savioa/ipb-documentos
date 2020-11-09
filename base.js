document.addEventListener('DOMContentLoaded', () => {
    var obsoletos = document.querySelectorAll('.obsoleta');
    var controle = document.querySelector('#mostrar_versoes');
    
    controle.addEventListener('change', (check) => {
        if (obsoletos.length > 0) {
            obsoletos.forEach(item => {
                item.classList.toggle('is-hidden');
            });
        }
    });

    var instrumentos = document.querySelectorAll('span[data-instrumento]');

    if (instrumentos.length > 0) {
        instrumentos.forEach(el => {
            var span = document.createElement('span');
            span.className = "tag is-light ml-2";
            span.appendChild(document.createTextNode(el.attributes['data-instrumento'].value));

            var alvo = el;

            if (el.firstElementChild.tagName === "DEL") {
                alvo = el.firstElementChild;
            }
            
            alvo.appendChild(span);
        });
    }
});