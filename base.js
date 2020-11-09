document.addEventListener('DOMContentLoaded', () => {
    var instrumentos = Array.prototype.slice.call(document.querySelectorAll('span[data-instrumento]'), 0);

    if (instrumentos.length > 0) {
        instrumentos.forEach(el => {
            var span = document.createElement('span');
            span.className = "tag is-light ml-2";
            span.appendChild(document.createTextNode(el.attributes['data-instrumento'].value));

            if (el.firstElementChild.tagName === "DEL") {
                el.firstElementChild.appendChild(span);
            }
            else {
                el.appendChild(span);
            }
        });
    }
});