$("#ChangePwdForm").submit(function (e) {
        e.preventDefault();
        alert('jjjj');
        $.ajax({
               type: 'POST',
               url: "../../admin/changepassword",
               data: {
                    OldPassword: $("#OldPwd").val(),
                    NewPassword: $("#NewPwd").val(),
                    AuthPassword: $("#AuthPwd").val()
               },
               success: function (response) {
                     if (response['message'] == 'Thao tác thành công!') {
                        alert('Thao tác thành công!');
                     }
                     else {
//                        $("#message").text($("#AuthPwd").val());
//                        alert($("#OldPwd").val());
                     }
               },
               error: function (response) {
<!--                  console.log(response)-->
               }
        });
});