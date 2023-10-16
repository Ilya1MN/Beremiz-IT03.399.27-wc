
import { Library } from "lib_element";
import * as sys from "@sys";
import {encode, decode} from "@sciter";
import { ToolbarButtonUpdate } from "./toolbar/tool-bar";


function GetFrameEditor()  { return document.$("frame#editor"); }

function GetFrameEditorApp(FrameEditor) { return FrameEditor.frame?.document.$("#editor_app"); }

function GetEditorApp(body_tree) { return body_tree.$("#editor_app"); }

function GetLibrary() { return document.body.$("#library"); }

function GetFramesetLibrary() { return document.body.$("frameset#frameset_library"); }

function GetLogger() { return document.$("debug_log"); }

export function GetTarget(target_name){
    let path_target = `${__DIR__}targets/${target_name}.json`
    let read_data = sys.fs.$readfile(URL.toPath(path_target))
    return JSON.parse(decode(read_data, "utf-8"));
}

export class AppStorage{
    constructor(){
        this.file_name = ''
        this.file_filter = 
        "SIM files only(*.json)|*.json|";
        this.path = null;
    }

    static Save_File(){
        let frame_editor = GetFrameEditor();
        if (frame_editor){
            let storage = new AppStorage();
            let editor = GetFrameEditorApp(frame_editor);
            let path = editor?.get_project_path()
            if (typeof(path) === "string"){
                return storage.save_file(path)
            }
            else{
                return storage.save_file_as();
            }
        }
        return false;
    }
    static Save_File_As(){
        let storage = new AppStorage();
        return storage.save_file_as();
    }
    static New_File(){
        let storage = new AppStorage();
        return storage.new_file();
    }

    static Open_File(){
        let storage = new AppStorage();
        return storage.open_file()
    }

    static _get_targets() {
      let targets = []
      for ( let script of sys.fs.$readdir(URL.toPath(`${__DIR__}targets/`)) ){
        if(script.name.indexOf('.json') + 1){
          targets.push(script.name.replace(".json",""));
        }
      }
      return targets;
    }

    static _write_storage(dir, data){
        const file = sys.fs.$open(URL.toPath(dir), "w+", 0o666);
        file.$write( encode(JSON.stringify(data, null, "  "), "utf-8") );
        file.$close();
    }

    static _read_storage(dir){
        let read_data = sys.fs.$readfile(URL.toPath(dir));
        let data = JSON.parse(decode(read_data, "utf-8"));
        return data;
    }

    static _save_storage(dir, save_data){
        let res = false;
        if (dir){
            AppStorage._write_storage(dir, save_data);
            res = true;
        }
        else{
            res = false;
        }
        return res;
    }

    open_storage(dir){
        let root = AppStorage._read_storage(dir);
        return root;
    }


    new_file(){
        return this.load_editor();
    }

    select_target(targets){
        var wnd = Window.this.modal({
            url   : __DIR__ + "targets/target_select_dialog.htm", 
            state : Window.WINDOW_SHOWN,
            width : 500,
            height: 150,
            //parameters: {settings: this.settings, set_settings: this.attrs}
            parameters: targets
        });
        return wnd;
    }

    load_editor(fn = undefined, root_storage = undefined){
        let frame_editor = GetFrameEditor();
        //frame_editor.on("complete", (evt) => evt.target.$("#editor_app").LoadElementsCache())
        //let isLoad = this.save_ask(frame_editor.frame.document);
        /*if(frame_editor.frame.document){
            frame_editor.frame.document = undefined;
        }*/
        frame_editor.frame.loadFile(URL.fromPath("editor/index.html"))
        let editor_doc = frame_editor.frame.document;
        if(editor_doc){
            let target_name = undefined
            let targets = AppStorage._get_targets();
            let logger = GetLogger();
            if (!root_storage)
            {
                target_name = this.select_target(targets);
            }
            else{
                for (let element of root_storage.elements)
                {
                    if(targets.indexOf(element.tagname) != -1){
                        target_name = element.tagname;
                        break;
                    }
                }
            }
            if(target_name)
            {
                editor_doc.globalThis["MbrtuStatusClass"] = globalThis["MbrtuStatusClass"]
                editor_doc.body.append(editor_doc.globalThis["Editor"]({storage: root_storage, path: fn, target: target_name, logger: logger}));
                document.body.addEventListener("keydown", (event) => {
                    
                    let editor = GetFrameEditorApp(GetFrameEditor())
                    //GetEditorApp(editor_doc.body)
                    editor.keydown(event)
                }, false);
                let library = GetLibrary()
                if (library === undefined || library == null){
                    GetFramesetLibrary().patch(<Library frame_doc={editor_doc}/>)
                }
                let editor_app = GetFrameEditorApp(GetFrameEditor());
                let plc_name = editor_app.plc_name

                //let editor = GetFrameEditorApp(GetFrameEditor())
                //editor.set_settings();


                Window.this.xcall("StartEditor", {plc_name: plc_name});
                ToolbarButtonUpdate(false)
                return true;
            }
            else{
                logger.write_error("Plc configuration not found");
            }
        }
        
        return false;
    }

    open_file(){
        if(this.path == null)
        {
            this.path = Window.this.xcall("GetProjectPath")
        }
        let fn = Window.this.selectFile({
            filter:this.file_filter,
            mode: "open",
            path: (this.path) ? URL.toPath(this.path) : URL.toPath(__DIR__)
        });
        if(fn){
            let root = this.open_storage(fn);
            return this.load_editor(fn, root);
        }
        
    }

    save_file(dir){
        let frame_editor = GetFrameEditor();
        let editor = GetFrameEditorApp(frame_editor);
        if (editor)
        {
            let editor_data = editor.get_storage()
            AppStorage._save_storage(dir, editor_data)
            return true;
        }
        return false;
    }

    save_file_as(){
        let fn = Window.this.selectFile({
            filter: this.file_filter,
            mode:"save",
            //path: URL.toPath(__DIR__ + "load-save-file.docx")
            path: URL.toPath(__DIR__)
        });
        this.save_file(fn)
    }
}
