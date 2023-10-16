
import { MenuBar } from "menu/menu-bar.js";
import { ToolBar } from "toolbar/tool-bar.js";
import { Plc } from "./editor/generete_svg_plc";
import { AppStorage } from "./storage";
import { MbrtuStatus } from "./status_bar/mbrtu-status";


document.body.$("#ToolBar").append(<MenuBar />)
document.body.$("#ToolBar").append(<ToolBar />)
document.body.$("#StatusBar").append(<MbrtuStatus />)
//document.body.$("#log").append(<DebugLog />)

document.on("InterfaceDO", function(params) {
  Plc.InterfaceDO(params.data.pin_num, params.data)
  return true
});

document.on("MBRTU_Status", function(params) {
  if (globalThis["MbrtuStatusClass"])
  {
    globalThis["MbrtuStatusClass"].setStatus(params.data.mbrtuIsRun)
  }
  return true;
  
});

document.on("InterfaceAO", function(params) {
  Plc.InterfaceAO(params.data.pin_num, params.data)
  return true
});

document.on("add_mbrtu_log", function(evt){
  let mbrtu_log = document.body.$("tbody")
  mbrtu_log.write(evt.data);
});

document.on("NativeCallClose", ()=> Window.this.close());

document.on("closerequest", CloseWindow);

function CloseWindow(evt)
{
  let frame_editor = document.$("frame#editor")
  let isSave = false;
  if(frame_editor.frame.document)
  {
    
    let editor_app = frame_editor.frame.document.$("#editor_app")
    if(editor_app.constructor.name == "Editor")
    {
      isSave = true;
      let new_storage = editor_app.get_storage();
      let path = editor_app.get_project_path();
      
      if (typeof path === 'string') 
      { 
        var old_storage = AppStorage._read_storage(path); 
        if (new_storage != null && typeof new_storage === 'object' && old_storage != null && typeof old_storage === 'object')
        {
          let old_storage_string = JSON.stringify(old_storage, null, "  ");
          let new_storage_string = JSON.stringify(new_storage, null, "  ");
          
          isSave = new_storage_string !== old_storage_string;
        }
      }
    }

    if(isSave)
    {
      const question_str = @"There are changes, do you want to save?";
      const yes_str = @"Yes";
      const no_str  = @"No";
      var r = Window.this.modal( <question caption={@"Save"}>
                                    <content>{question_str}</content>
                                    <buttons>
                                      <button id="yes" role="default-button">{yes_str}</button>
                                      <button id="no" role="cancel-button">{no_str}</button>
                                    </buttons>
                                  </question>);

      if(r == "yes"){
        AppStorage.Save_File();
      }
    }
  }
}

Window.this.requestAttention("stop")