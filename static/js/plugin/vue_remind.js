jQuery.extend( jQuery.easing,
    {
        easeOutBounce: function (x, t, b, c, d) {
            if ((t/=d) < (1/2.75)) {
                return c*(7.5625*t*t) + b;
            } else if (t < (2/2.75)) {
                return c*(7.5625*(t-=(1.5/2.75))*t + .75) + b;
            } else if (t < (2.5/2.75)) {
                return c*(7.5625*(t-=(2.25/2.75))*t + .9375) + b;
            } else {
                return c*(7.5625*(t-=(2.625/2.75))*t + .984375) + b;
            }
        },
    });
Vue.component("remind", {
    props: ['shown', 'duration', 'start_css', 'end_css'],
    data: function(){
        return {
            msg: '',
            state: '',
            shown: parseFloat(this.$props['shown']),
            duration: parseFloat(this.$props['duration']),
        }
    }, template: "<div class='remind'>" +
        "          <div class='bg'></div>" +
        "          <div class='show'><span :data-state='state'><span v-html='msg'></span></span></div>" +
        "          <div class='cover'></div>" +
        "      </div>",
    methods: {
        start: function(r){
            this.msg = r['msg'];
            this.state = r['state'];
            let vue_ = this;
            let remind = $(this.$el);
            let cover = remind.find('.cover');
            remind.stop();
            remind.css(vue_.$props['start_css']);
            cover.stop();
            cover.css({'left': '0'});
            remind.stop().animate(vue_.$props['end_css'], vue_.shown*1500, 'easeOutBounce', function () {
                cover.stop().animate({'left': '-100%'}, vue_.duration*1000, 'linear', function () {
                    remind.animate(vue_.$props['start_css'], vue_.shown*1000, 'linear', function () {
                        cover.css('left', '0');
                    })
                })
            })
        },
    }
});