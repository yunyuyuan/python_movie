$(document).ready(function () {
    let map = para_to_map();
    map['s'] = decodeURI(map['s']);
    let pg_count = 10;
    let vue_ = new Vue({
        el: '#container',
        data: {
            at: (map['t']==='cate'?'标签':'搜索'),
            s: map['s'],
            now_p: 1,
            info: [0, []]
        },
        computed: {
            p_count: function () {
                return Math.ceil(this.info[0]/pg_count);
            }
        },
        methods: {
            change_p: function (p) {
                vue_.now_p = p;
                get_list()
            }
        }
    });
    get_list();
    function get_list(){
        ajax_(function (r) {
            if (r['state']==='success'){
                vue_.info = r['data']
            }
        }, '/ajax/get_mv_list', {'t': map['t'], 's': map['s'], 'p': vue_.now_p-1, 'count': pg_count})
    }
});