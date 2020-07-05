Vue.component("turn-page", {
    props: ['now', 'count', 'show_count', 'event'],
    data: function(){
        return {
            now: parseInt(this.$props['now']),
            count: parseInt(this.$props['count']),
            show_count: parseInt(this.$props['show_count']),
            page_info: []
        }
    },
    watch: {
        now: function(){
            this.now = parseInt(this.$props['now'])
        },
        count: function () {
            let now = this.now,
                show_count = this.show_count,
                count = this.count = parseInt(this.$props['count']);
            let page_info = [];
            if (now <= count) page_info.push(now);
            for (let i=1;i<=show_count;i++) {
                if (now-i>0 && page_info.length<show_count && page_info.length<count){
                    page_info.splice(0, 0, now-i);
                }
                if (now+i<=count && page_info.length < show_count) {
                    page_info.push(now + i)
                }
            }
            this.page_info = page_info;
        }
    },
    template:
        "<div class='turn-page'>" +
        "   <a class='txt' :p='(count>0)?1:false' @click.prevent='do_turn'>首页</a>" +
        "   <a v-for='page in page_info' :key='page' :p='page' @click.prevent='do_turn' :class='{active: now==page}'>{{ page }}</a>" +
        "   <a class='txt' :p='(count>0)?count:false' @click.prevent='do_turn'>尾页</a>" +
        "</div>",
    methods: {
        do_turn: function(e){
            let a = e.target;
            if (a.hasAttribute('p')){
                this.$emit(this.$props['event'], parseInt(a.getAttribute('p')));
            }
        }
    }
});