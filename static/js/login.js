$(document).ready(function () {
    let vue_ = new Vue({
        el: '#container',
        data: {
            who_list: ['用户', '管理员', '超级管理员'],
            act: '',
            pwd: '',
            at: '用户'
        },
        methods: {
            change_at: function (e) {
                vue_.at = e.target.innerText;
            },
            to_pwd: function(e){
                e.target.parentElement.nextElementSibling.querySelector('input').focus();
            },
            do_submit: function () {
                if (vue_.act==='' || vue_.pwd===''){
                    head_vue.remind_err('账号或密码不能为空')
                }
                ajax_(function (r) {
                    head_vue.remind(r);
                    if (r['state']==='success'){
                        let map = para_to_map();
                        setTimeout(function () {
                            location.href = (typeof map['url'] != 'undefined'?map['url']:'/')
                        }, 500)
                    }
                }, '/ajax/login', {'act': vue_.act, 'pwd': hex_md5(vue_.pwd), 'at': vue_.at})
            }
        }
    })
});