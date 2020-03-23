
    var open = false;
    $('#nav-btn').click(function (){
                // 按钮状态
        $(this).css("background-color", open ? '#333' : '#222');
        var navBar = $('.nav-bar');
                // 设置header的高度，将导航列表显示出来
        var height = navBar.offset().top + navBar.height();
        $('#header').animate({
            height: open ? 50 : height
        });
                // 修改开关状态
        open = !open;
    });

