class SaveDialog extends Element{
    form_name = "targets";
    save_ask_msg = @"There are changes, do you want to save?";

    constructor(){
        super();
    }
    render(){
        return  (<div class="parameter">
                    <div class="title">
                        <p>{this.save_ask_msg}</p>
                    </div>
                        <div class="buttons">
                        <button.cmd.yes>Yes</button>
                        <button.cmd.no>No</button>
                        
                    </div>
                </div>);
    }
//<button.cmd.cancel>Cancel</button>
    ["on click at button.cmd.yes"](){
        Window.this.close(true);
    }
    ["on click at button.cmd.no"](){
        Window.this.close(false);
    }
    /*["on click at button.cmd.cancel"](){
        Window.this.close();
    }*/

}


document.body.append(<SaveDialog/>)