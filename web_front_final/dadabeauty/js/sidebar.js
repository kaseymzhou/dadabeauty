//设置边栏头像、名字、个性签名
var img = window.localStorage.getItem('dabeauty_img')
var username = window.localStorage.getItem('dabeauty_user')
var person_desc = window.localStorage.getItem('dabeauty_desc')
if (img && username && person_desc){
    $('#sidebar_profile').attr('src',img);
    $('#sidebar_username').text(username);
    $('#sidebar_descript').text(person_desc);
}