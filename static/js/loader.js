var loader = document.querySelector('.loader');
var main = document.querySelector('.main');
$(window).ready(
    function () {
        setTimeout(
            function () {
                loader.style.opacity = 0;
                loader.style.display = 'none';
                main.style.display = 'block';
                setTimeout(function () { main.style.opacity = 1; }, 50)
            }, 500)
    }
);
