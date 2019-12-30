// header显示用户头像以及名字
var header_name = window.localStorage.getItem('dabeauty_user')
var uid = window.localStorage.getItem('dabeauty_uid') 
var img = window.localStorage.getItem('dabeauty_img') 
if (header_name && uid){
    $('#header_logged').css({display:"block"});
    $('#header_unlogged').css({'display':'none'});
    $('#header_img').attr('src',img);
    $('#header_name').text(header_name);
}
// 登出功能
$('#logout').click(function(){
    window.localStorage.clear();
        alert('退出登录');
        window.location.href = 'index.html'
})
