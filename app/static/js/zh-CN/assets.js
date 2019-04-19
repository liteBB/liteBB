function del() {
    var msg = "您确定删除吗？";
    if (confirm(msg)==true)
    {
        return true;
    }
    else
    {
        return false;
    }
}


function like(obj, post_id){
    $.ajax({
        url:'/like',
        data:{ postid:post_id },
        type:'POST',
        success:function(callback){
            if(callback !== '-1'){
                var result = '<a><img class="like-icon" src="/static/icons/liked.svg"></a>' + ' ' + callback;
                $(obj).html(result)
            }
            else{
                alert("抱歉，请重试！")
            }
        },
        error:function(){
            alert("Error, please contact info@litebb.com")
        }
    });
}

