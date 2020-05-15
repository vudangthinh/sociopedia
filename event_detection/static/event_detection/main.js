$(document).ready(function () {

    $("#sidebar").mCustomScrollbar({
         theme: "minimal"
    });

    $('#sidebarCollapse').on('click', function () {
        $('#sidebar, #content').toggleClass('active');
    });

    $('#sidebar ul li').on('click', function () {
        $('#sidebar ul .active').removeClass('active');
        $(this).addClass('active');
    });

});