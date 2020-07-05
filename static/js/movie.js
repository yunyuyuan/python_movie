$(document).ready(function () {
    let mv_id = location.pathname.replace(/.*\/(\d+)$/, '$1');
    let ev_p_count = 15;
    let vue_ = new Vue({
        el: '#container',
        data: {
            mv_id: mv_id,
            now_ep: '',
            info: {'cov': 'default.jpg', 'info': ['','','','',''], 'src': [0,[]], 'star':2.5, 'cate':[]},
            info_lis: mv_info_lis,
            ev_p: 1,
            ev_data: [0,[]],
            wrt_star: 5,
            ev_txt: ''
        },
        computed: {
            p_count: function () {
                return Math.ceil(this.ev_data[0]/ev_p_count);
            }
        },
        methods: {
            swc_ep: function (i) {
                vue_.now_ep = vue_.info['src'][i]
            },
            give_star: function (star) {
                vue_.wrt_star = parseFloat((star[1]*5).toString().replace(/(\d\.\d).*/, '$1'));
            },
            submit_ev: function () {
                if (vue_.ev_txt === ''){
                    head_vue.remind_err('评论不能为空')
                }else{
                    ajax_(function (r) {
                        head_vue.remind(r);
                        get_ev()
                    }, '/user/add_ev', {'id': mv_id, 'star': vue_.wrt_star, 'ev': vue_.ev_txt})
                }
            },
            change_p: function (p) {
                vue_.ev_p = p;
                get_ev()
            }
        }
    });
    get_ev();
    function get_ev(){
        ajax_(function (r) {
            if (r['state'] === 'success'){
                vue_.ev_data = r['data']
            }
        }, '/ajax/get_ev', {'id': mv_id, 'p': vue_.ev_p-1, 'count': ev_p_count})
    }
    ajax_(function (r) {
        if (r['state']==='success'){
            document.title = r['data']['title'];
            for (let s of ['info','src','cate']){
                r['data'][s] = JSON.parse(r['data'][s]);
            }
            vue_.now_ep = r['data']['src'][0];
            vue_.$refs['mv_star'].update_percent(r['data']['star']);
            vue_.info = r['data'];
        }
    }, '/ajax/mv_detail', {'id': mv_id})
});