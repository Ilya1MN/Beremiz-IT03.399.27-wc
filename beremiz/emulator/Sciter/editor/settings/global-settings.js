export class GlobalSettings{
    
    settings = [{type: "text", parameter_name: "Hostname", value: "default"}, {type: "number", parameter_name: "Port", value: 1, max_value: 65535, min_value: 0, step: 1},];
    def_attrs = {"Hostname": "localhost", "Port": 3000};

    constructor(props){
        this.attrs = Window.this.xcall("PYRO_GetSettings");
    }
    load_window(){
        if (this.settings){            
            var wnd = Window.this.modal({
                url   : __DIR__ + "global-settings.htm", 
                state : Window.WINDOW_SHOWN,
                parameters: {settings: this.settings, set_settings: this.attrs}
            });
            if(wnd){
                return wnd;
            }
        }
        return undefined;
    }
}