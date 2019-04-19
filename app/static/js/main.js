function preview_off() {
    document.getElementById('flask-pagedown-content-preview').style.display='none';
    document.getElementById('md-0').style.display='none';
    document.getElementById('md-1').style.display='block';
}

function preview_on() {
    document.getElementById('flask-pagedown-content-preview').style.display='block';
    document.getElementById('md-0').style.display='block';
    document.getElementById('md-1').style.display='none';
}

function moderate(obj, comment_id){
    $.ajax({
        url:'/admin/moderate',
        data:{ commentid:comment_id },
        type:'POST',
        success:function(callback){
            if(callback === '0'){
                var result_0 = '<span class="glyphicon glyphicon-ban-circle" style="color: #dd0000;" aria-hidden="true"></span>';
                $(obj).html(result_0)
            }
            else if(callback === '1'){
                var result_1 = '<span class="glyphicon glyphicon-ok" style="color: #25b864;" aria-hidden="true"></span>';
                $(obj).html(result_1)
            }
            else{
                alert("Please try again!")
            }
        },
        error:function(){
            alert("Error, please try again!")
        }
    });
}

