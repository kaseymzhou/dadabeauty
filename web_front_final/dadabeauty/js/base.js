$(function () {
    var nav = $("#top"); //得到导航对象
    var win = $(window); //得到窗口对象
    var sc = $(document); //得到document文档对象。
    win.scroll(function () {
        if (sc.scrollTop() >= 60) {
            nav.addClass("fixed_nav");
        } else {
            nav.removeClass("fixed_nav");
        }
    })
})