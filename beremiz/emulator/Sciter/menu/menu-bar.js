import { AppStorage } from '../storage';

export class MenuBar extends Element {

    new_file_title = @"New file";
    open_file_title = @"Open file";
    save_file_title = @"Save file";
    save_file_as_title = @"Save file as...";
    copy_title = @"Copy";
    cut_title = @"Cut";
    paste_title = @"Paste";
    file_title = @"File";
    edit_title = @"Edit";

    constructor(){
        super();
    }

    ["on click"](evt){
        switch(evt.target.name){
            case "new-file":
                AppStorage.New_File();
                break;
            case "open-file":
                AppStorage.Open_File()
                break;
            case "save-file":
                AppStorage.Save_File()
                break;
            case "save-file-as":
                AppStorage.Save_File_As();
                break;
        }
    }
    render() {
        
        return <ul styleset={__DIR__ + "menu-bar.css#menu-bar"}>
            <li>{this.file_title}
                <menu>
                  <li.command name="new-file" accesskey="^N">{this.new_file_title}<span class="accesskey">Ctrl+N</span></li>
                  <li.command name="open-file">{this.open_file_title}</li>
                  <li.command name="save-file">{this.save_file_title}</li>
                  <li.command name="save-file-as">{this.save_file_as_title}</li>
                </menu>
            </li>
            
        </ul>;
    }

}