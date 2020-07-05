$(document).ready(function () {
    let vue_ = new Vue({
        el: '#manage-menu',
        data: {
            path: location.pathname.replace(/.*\/(.*?)$/, '$1'),
        },
        methods: {
            logout: function(){
                if (confirm('确认登出?')){
                    ajax_(function (r) {
                        head_vue.remind(r);
                        if (r['state']==='success'){
                            location.href = '/login'
                        }
                    }, '/ajax/logout')
                }
            },
        }
    })
});