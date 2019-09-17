let vm = new Vue({
    el: '#app',
    // 修改Vue读取变量的语法
    delimiters: ['[[', ']]'],
    data: {
        username: '',		// 用户名
        password: '', 		// 密码
        password2: '',		// 确认密码
        mobile: '',			// 手机号
        allow: '',			// 同意协议
        uuid: '',			// uuid
        image_code: '',
        image_code_url: '',  // 图形验证码请求地址
        sms_code_tip: '获取短信验证码',


        error_name: false,
        error_password: false,
        error_password2: false,
        error_mobile: false,
        error_allow: false,
        error_image_code: false,
        sending_flag: false,    // 来判定重复点击的

        error_name_message: '',		// 用户名错误提示
        error_mobile_message: '',	// 密码错误提示
        error_image_code_message: '', // 验证码错误提示
    },
    // 当页面加载结束，加载图片验证码
    mounted() {
        // 生成图形验证码
        this.generate_image_code();

    },
    methods: {

        // 校验短信验证码
        send_sms_code() {
            // 判断是否重复点击
            if (this.sending_flag == true) {
                return;
            }

            // 校验图形验证码和校验手机号参数
            this.check_mobile();
            this.check_image_code();
            // 假如有一个参数不对就回退
            if (this.error_mobile == true || this.error_image_code == true) {
                this.sending_flag == false;
                return;
            }

            // ajax请求验证码
            let url = 'sms_codes/' + this.mobile + '/?image_code=' + this.image_code + '&uuid=' + this.uuid;
            axios.get(url, {
                responseType: "JSON"
            })
                .then(response => {
                    // 判断后端响应的类型
                    alert(response.data.code);
                    if (response.data.code == 0) {
                        //响应成功，开始倒计时
                        let num = 60;
                        let t = setInterval(() => {
                            // 当倒计时到最后1秒的时候，结束这个函数
                            if (num == 1) {
                                clearInterval(t);
                                this.sms_code_tip = '获取短信验证码';
                                // 刷新验证码
                                this.generate_image_code();
                                this.sending_flag = false;
                            } else {
                                num -= 1;
                                // 展示秒数
                                this.sms_code_tip = num + '秒';
                            }
                        }, 1000)
                    } else {
                        if (response.data.code == 4001) {
                            this.error_image_code_message = response.data.errmsg;
                            this.error_image_code = true;
                        } else if (response.data.code == 4002) {
                            this.error_image_code_message = response.data.errmsg;
                            this.generate_image_code();
                            this.error_image_code = true;
                        }
                        this.sending_flag = false;
                    }

                })
                // 响应失败则操作台打印错误信息
                .catch(error => {
                    console.log(error.response);
                })

        },

        // 生成图形验证码
        generate_image_code() {
            // 生成uuid
            this.uuid = generateUUID();
            this.image_code_url = '/image_codes/' + this.uuid + '/';
        },

        // 校验验证码
        check_image_code() {
            if (this.image_code.length != 4) {
                if (this.image_code.length == 0) {
                    this.error_image_code_message = '验证码不能为空';
                    this.error_image_code = true;
                } else {
                    this.error_image_code_message = '验证码格式不正确';
                    this.error_image_code = true;
                }

            } else {
                this.error_image_code = false;
            }
        },

        // 校验用户名
        check_username() {
            // 准备正则表达式
            let re = /^[a-zA-Z0-9_-]{5,20}$/;
            // 正则表达式匹配用户名
            if (re.test(this.username)) {
                this.error_name = false;

                if (this.error_name == false) {
                    let url = '/usernames/' + this.username + '/count/'
                    axios.get(url, {
                        responseType: JSON
                    })
                        .then(response => {
                            if (response.data.count == 1) {
                                this.error_name_message = "用户名已存在";
                                this.error_name = true;
                            } else {
                                this.error_name = false;
                            }
                        })
                        .catch(error => {
                            console.log(error.response);
                        })

                }


            } else {
                this.error_name = true;
                this.error_name_message = '请输入5-20个字符的用户名';
            }
        },
        // 校验密码
        check_password() {
            let re = /^[0-9A-Za-z]{8,20}$/;
            if (re.test(this.password)) {
                this.error_password = false;
            } else {
                this.error_password = true;
            }
        },

        // 校验确认密码
        check_passwork2() {
            // 判断两次密码是否一致
            if (this.password != this.password2) {
                this.error_password2 = true;
            } else {
                this.error_password2 = false;
            }
        },
        // 校验手机号
        check_mobile() {
            let re = /^1[3-9]\d{9}$/;
            if (re.test(this.mobile)) {
                this.error_mobile = false;

                if (this.error_mobile == false) {
                    url = '/mobiles/' + this.mobile + '/count/'
                    axios.get(url, {
                        responseType: JSON
                    })
                        .then(response => {
                            if (response.data.count == 1) {
                                this.error_mobile_message = "该号码已被注册";
                                this.error_mobile = true;
                            } else {
                                this.error_mobile = false;
                            }
                        })
                        .catch(error => {

                        })
                }


            } else {
                this.error_mobile_message = '您输入的手机号格式不正确';
                this.error_mobile = true;
            }
        },
        // 校验是否勾选协议
        check_allow() {
            if (!this.allow) {
                this.error_allow = true;
            } else {
                this.error_allow = false;
            }
        },
        // 监听表单提交事件
        on_submit() {
            this.check_username();
            this.check_password();
            this.check_passwork2();
            this.check_mobile();
            this.check_allow();

            if (this.error_name == true || this.error_password == true || this.error_password2 == true
                || this.error_mobile == true || this.error_allow == true) {
                // 禁用表单的提交
                window.event.returnValue = false;
            }
        },
    }
});