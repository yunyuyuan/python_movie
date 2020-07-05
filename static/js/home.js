$(document).ready(function () {
    let vue_ = new Vue({
        el: '#container',
        data: {
            swp: [],
            pos: 0,
            hot: [],
            cate: [],
        },
        computed: {
        },
        methods: {
            do_swp: function (s, i) {
                let len = vue_.swp.length;
                if (s==='orient'){
                    if (vue_.pos+i < 0){
                        vue_.pos = vue_.swp.length-1;
                    }else if (vue_.pos+i > vue_.swp.length-1){
                        vue_.pos = 0
                    }else{
                        vue_.pos += i;
                    }
                }else{
                    vue_.pos = i-1;
                }
            }
        }
    });
    ajax_(function (r) {
        if (r['state']==='success'){
            vue_.swp = JSON.parse(r['data'][0][0]);
            vue_.cate = JSON.parse(r['data'][0][1]);
            vue_.hot = r['data'][1]
        }
    }, '/ajax/get_home');

});