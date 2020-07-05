Vue.component('star', {
    props: ['star', 'modify', 'f_size', 'event'],
    data: function(){
        return {
            percent: parseFloat(this.$props['star'])/5,
            can_modify: this.$props['modify']!=='f',
        }
    },
    template: "" +
        "<div class='star'>" +
        "   <span :style='{width: percent*100+\"%\", fontSize: f_size}' @mousemove='check_change'></span>" +
        "</div>"
    ,
    methods: {
        check_change: function(e){
            if(this.can_modify){
                this.percent = e.offsetX/this.$el.offsetWidth;
                if (typeof this.$props['event']!='undefined') {
                    this.$emit(this.$props['event'], [this.$el, this.percent]);
                }
            }
        },
        update_percent: function (star) {
            this.percent = parseFloat(star)/5;
        }
    }
});