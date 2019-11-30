$(document).ready(function () {
    $('.drop').on('dragover', function(e){
        e.preventDefault();
    });
    $('.drag').on('dragstart', function(e) {
        e.originalEvent.dataTransfer.setData('object', e.target.id);
    });
    $('.drop').on('drop', function(e) {
        e.preventDefault();
        var data = e.originalEvent.dataTransfer.getData('object');
        e.target.appendChild(document.getElementById(data));
        $(this).off('dragover drop');
    });
});