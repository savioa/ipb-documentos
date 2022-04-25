document.addEventListener('keyup', (e) => {
    if (e.ctrlKey && e.key == 'i') {
        document.querySelector('#ir').focus();
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);

    if ($navbarBurgers.length > 0) {

        $navbarBurgers.forEach(el => {
            el.addEventListener('click', () => {
                const $target = document.querySelector('.navbar-menu');

                el.classList.toggle('is-active');
                $target.classList.toggle('is-active');

            });
        });
    }

    function openModal($el) {
        $el.classList.add('is-active');
    }

    function closeModal($el) {
        $el.classList.remove('is-active');
    }

    (document.querySelectorAll('.posicao') || []).forEach(($trigger) => {
        const $target = document.getElementById('modal');

        $trigger.addEventListener('click', (event) => {
            const modal = document.querySelector('.modal-content');

            modal.innerHTML = Array.from(event.target.parentElement.parentElement.children).filter(c => c.classList.contains('bloco_anotacoes') && c.getAttribute('data-posicao') == event.target.textContent)[0].outerHTML.replace(' is-hidden', '');
            
            document.querySelectorAll('.modal-content a').forEach(
                function(currentValue, currentIndex, listObj) {
                    currentValue.addEventListener('click', (event) => {
                        const $target = document.getElementById('modal');
                        closeModal($target);
                    });
                },
                ''
            );

            openModal($target);
        });
    });

    (document.querySelectorAll('.modal-background, .modal-close, .modal-card-head .delete, .modal-card-foot .button') || []).forEach(($close) => {
        const $target = document.getElementById('modal');

        $close.addEventListener('click', () => {
            closeModal($target);
        });
    });

    document.addEventListener('keydown', (event) => {
        const e = event || window.event;

        if (e.keyCode === 27) {
            const $target = document.getElementById('modal');
            closeModal($target);
        }
    });

    document.querySelector('#mostrar_versoes').addEventListener('change', () => {
        const obsoletos = document.querySelectorAll('.obsoleta');

        if (obsoletos.length > 0) {
            obsoletos.forEach(item => {
                item.classList.toggle('is-hidden');
            });
        }
    });

    document.querySelector('#mostrar_anotacoes').addEventListener('change', () => {
        const obsoletos = document.querySelectorAll('.posicao');

        if (obsoletos.length > 0) {
            obsoletos.forEach(item => {
                item.classList.toggle('is-hidden');
            });
        }
    });

    document.querySelector('#ir').addEventListener('keyup', (e) => {
        if (e.code == 'Enter' || e.code == 'NumpadEnter') {
            const $menu = document.querySelector('.navbar-menu');
            $menu.classList.remove('is-active');

            const $burger = document.querySelector('.navbar-burger');
            $burger.classList.remove('is-active');

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