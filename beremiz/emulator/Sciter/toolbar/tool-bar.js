import { AppStorage } from '../storage';
import { GlobalSettings } from '../editor/settings/global-settings';

export function ToolbarButtonUpdate(start){    
    let run_btn = document.body.$("button.cmd.run");
    let pause_btn = document.body.$("button.cmd.pause");
    let stop_btn = document.body.$("button.cmd.stop");
    run_btn.disabled = start;
    pause_btn.disabled = !start;
    stop_btn.disabled = !start;
}

export class ToolBar extends Element {
    new_file_title = @"New file";
    open_file_title = @"Open file";
    save_file_title = @"Save file";
    save_file_as_title = @"Save file as...";
    run_softplc_title = @"Run SoftPlc";
    pause_softplc_title = @"Suspend SoftPlc";
    stop_softplc_title = @"Stop SoftPlc";
    settings_title = @"Settings"
    
    constructor(){
        super();
    }

    ["on click at button.cmd.new-file"]() {
        return AppStorage.New_File();
    }

    ["on click at button.cmd.open-file"]() {
        return AppStorage.Open_File();
    }

    ["on click at button.cmd.save-file"]() {
        return AppStorage.Save_File();
    }

    ["on click at button.cmd.save-file-as"]() {
        return AppStorage.Save_File_As();
    }

    ["on click at button.cmd.run"]() {
        let frame_editor = document.$("frame#editor").frame.document.$("#editor_app");
        //let editor = GetFrameEditorApp(GetFrameEditor())
        frame_editor.set_settings();
        Window.this.xcall("StartEmulation", {plc_name: frame_editor.get_target_name()})
        frame_editor.set_read_only(true);
        frame_editor.init_run_emulator();
        ToolbarButtonUpdate(true);
        return true;
    }

    ["on click at button.cmd.pause"](){
        Window.this.xcall("PauseEmulation")
        let frame_editor = document.$("frame#editor").frame.document.$("#editor_app");
        frame_editor.set_read_only(false);
        ToolbarButtonUpdate(false);
        return true;
    }

    ["on click at button.cmd.stop"](){
        Window.this.xcall("StopEmulation")
        let frame_editor = document.$("frame#editor").frame.document.$("#editor_app");
        frame_editor.set_read_only(false);
        ToolbarButtonUpdate(false);
        return true;
    }

    ["on click at button.cmd.settings"](){
        let sett = new GlobalSettings; 
        Window.this.xcall("SetSettingsSciter", sett.load_window())
    }

    render() {
        return <toolbar styleset={__DIR__ + "tool-bar.css#tool-bar"}>
          <button.cmd.new-file title={this.new_file_title} />
          <button.cmd.open-file title={this.open_file_title} />
          <button.cmd.save-file title={this.save_file_title} />
          <button.cmd.save-file-as title={this.save_file_as_title} />
          <button.cmd.settings title={this.settings_title} />
          <button.cmd.run disabled={true} title={this.run_softplc_title} />
          <button.cmd.pause disabled={true} title={this.pause_softplc_title} />
          <button.cmd.stop disabled={true} title={this.stop_softplc_title} />
        </toolbar>;
    }

}