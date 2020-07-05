let head_vue;
let mv_info_lis = ['导演', '编剧', '上映时间', '制片国家'];
$(document).ready(function () {
    head_vue = new Vue({
        el: '#-head',
        data: {
            s: '',
        },
        computed: {
        },
        methods: {
            go_search: function(){
                location.href = '/list?t=sc&s='+encodeURI(this.s);
            },
            remind: function (s) {
                this.$refs['head_remind'].start(s)
            },
            remind_err: function (s) {
                this.$refs['head_remind'].start({'state': 'error', 'msg': s})
            }
        }
    })
});

function para_to_map() {
    let map = {};
    let lis = location.search.match(/[?&](.+?)=(.*?)(?=&|$)/g);
    if (lis != null) {
        for (let m of lis) {
            map[m.replace(/[?&](.+?)=.*/, '$1')] = m.replace(/[?&].+?=(.*)/, '$1');
        }
    }
    return map;
}
// ajax函数
function ajax_(callback, url, data, option){
    let options = {
        success: function (r) {
            callback(r)
        },
        url: url, type: 'POST', dataType: 'json',
        data: (data)?data:{}
    };
    if (typeof options!='undefined'){
        Object.assign(options, option);
    }
    $.ajax(options)
}