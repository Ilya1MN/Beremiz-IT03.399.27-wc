class FormElementSettings extends Element {
    constructor(props, kids) {
        super();
        this.kids = kids;
        this.element_settings = Window.this.parameters.set_settings;
    }

    get_parameters(attrs){
        let form_settings = new Array();
        for (let attr of attrs){
            switch(attr.type){
                case "drop_list":
                    form_settings.push( set_drop_list(attr, this.element_settings) );
                    break;
                case "radio_button":
                    form_settings.push( set_radio_button(attr, this.element_settings) );
                    break;
                case "number":
                    form_settings.push( set_field(attr, this.element_settings, 22) )
                    break;
                default:
                    form_settings.push( set_field(attr, this.element_settings) );
                    break;
            }
        }
        return <form>{form_settings}<div class="submit_btn"><button type="submit">Ok</button> </div> </form>

        function set_field(data, set_data, height=20){
            let value;
            if (set_data){
                value = set_data[data.parameter_name];
            }
            return <div class="parameter"><label for={data.parameter_name}>{data.parameter_name}  </label>
                <input class="settings" type={data.type} id={data.parameter_name} name={data.parameter_name}
                min={data.min_value} max={data.max_value} value={value} step={data.step} style={`height: ${height}; width: 100px; text-align: left;`}/></div>;
        }
        
        function set_drop_list(data, set_data){
            let selected_el = new Array();
            let default_param;
            if (set_data){
                default_param = set_data[data.parameter_name];
            }
            let options_el = data.options;
            if (data.get_params_callback){
                options_el = data.get_params_callback()
            }
            for (let option of options_el){
                if (default_param){
                    if ( default_param == option ){
                        selected_el.push(<option selected>{option}</option>)
                        continue;
                    }
                }
                selected_el.push(<option>{option}</option>)
            }
            return (<div class="parameter">
                        <label for={data.parameter_name}>{data.parameter_name}</label>
                        <select name={data.parameter_name} class="settings"> {selected_el} </select>
                    </div>)
        }
        
        function set_radio_button(data, set_data){
            let selected_el = new Array();
            let default_param;
            if (set_data){
                default_param = set_data[data.parameter_name];
            }
            let options_el = data.options;
            if (data.get_params_callback){
                options_el = data.get_params_callback()
            }
            for (let option of options_el){
                if (default_param){
                    if ( default_param == option ){
                        selected_el.push(<button type="radio" value={option} 
                                                 name={data.parameter_name} class="settings"
                                                 checked>{option}
                                         </button>);
                        continue;
                    }
                }
                selected_el.push(<button type="radio" value={option} name={data.parameter_name} class="settings">{option}</button>);
            }
            return (<div class="parameter">
                        <label for={data.parameter_name}>{data.parameter_name}  </label>
                        {selected_el}
                    </div>)
        }
    }

    render(){
        return <div id="Settings">{this.get_parameters(Window.this.parameters.settings)}</div>;
    }
    

    ["on ^submit"](evt, form) {
        let attrs = Window.this.parameters.settings;
        let isClose = true;
        let err = new String();
        for(let attr of attrs)
        {
            if (attr.type == "number")
            {
                if (typeof attr.min_value === "number" && typeof attr.max_value === "number")
                {
                    let form_val = form.value[attr.parameter_name];
                    if(typeof form_val === "number" )
                    {
                        if (form_val < attr.min_value) 
                        {
                            isClose = false;
                            err = @"Unable to set parameter value: " + "\"" + attr.parameter_name + "\". " + @"The number is less than the minimum!\n";
                            break;
                        }
                        else if(form_val > attr.max_value)
                        {
                            isClose = false;
                            err = @"Unable to set parameter value: " + "\"" + attr.parameter_name + "\". " + @"The number is greater than the maximum!\n";
                            break;
                        }
                    }
                    else 
                    {
                        isClose = false;
                        err = @"Unable to set parameter value: " + "\"" + attr.parameter_name + "\". " + @"Parameter is not set!\n";
                        break;
                    }
                }
            }
            

        }

        if(isClose)
        {
            Window.this.close(form.value);
        }
        else 
        {
            var r = Window.this.modal(  <error caption={@"Error"}>
                                            <p>{@"Error set parameter: "}</p>
                                            <p>{err}</p>
                                        </error>)
        }
                
    }
}

document.body.append(<FormElementSettings/>);
