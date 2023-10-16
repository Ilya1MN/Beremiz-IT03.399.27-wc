class TargetSelector extends Element{
    form_name = "targets";
    target_label = @"Select target plc: ";
    constructor(){
        super();
        //this.plc_targets_vdom = [];
        let selected_list = []
        for(let target_name of Window.this.parameters){
            selected_list.push(<option>{target_name}</option>)
        }
        this.plc_targets_vdom = <div class="parameter">
                                    <label for={this.form_name}>{this.target_label}</label>
                                    <select name={this.form_name} class={this.form_name}> {selected_list} </select>
                                </div>
    }
    render(){
        return <form>{this.plc_targets_vdom} <button class="submit_btn" type="submit">Ok</button></form>
    }

    ["on ^submit"](evt, form) {
        if(form.value[this.form_name]){
            Window.this.close(form.value[this.form_name]);
        }
    }
}


document.body.append(<TargetSelector/>)