import { ConnectorLine } from "./connectorLine";

function GetEditorApp()  { return document.body.$("#editor_app"); }

export class Connectors extends Element{
    constructor(props) {
        super();
        this.viewBox = {x: Number.MAX_SAFE_INTEGER, y: Number.MAX_SAFE_INTEGER, x_max: 0, y_max: 0};
        this.lines = new Array();
        if (props.storage){
            this.set_storage(props.storage);
        }
    }

    set_storage(connectors_data){ 
        for (let data of connectors_data){
            let line = new ConnectorLine({id: data.id, x: data.x, y: data.y, target: data.first_target.target, channel: data.first_target.ch, first_direction: data.first_target.direction});
            line.set_second_target(data.second_target.target, data.second_target.ch, data.second_target.direction);
            line.set_lines(data.lines);
            this.lines.push(line);
        }
    }

    static _AddConnector(params){
        if(params.lines && params.line && params.this){
            params.this[params.lines].push(params.line);
            return {command: Connectors._DeleteConnector, parameters: { this: params.this, lines: params.lines }}
        }
    }

    static _DeleteConnector(params){
        if(params.this && params.lines){
            let line = params.this[params.lines].pop()
            return {command: Connectors._AddConnector, parameters: {this: params.this, lines: params.lines, line: line}}
        }
    }

    append_connector(line) {
        let editor = GetEditorApp()
        
        this.lines.push(line)
        editor.undo.push([{command: Connectors._DeleteConnector, parameters: {this: this, lines: "lines"}}])
        return true;
    }

    get_line(i) {
        return this.lines[i];
    }

    get_last_line(){
        return this.lines[this.lines.length - 1];
    }

    onmove_line(evt, lines, editor) {
        for (let line of lines){
            let cursor_data = set_resize_cursor(evt, line.GetRectsPath());
            if (cursor_data.resize){
                
                if (cursor_data.index){
                    editor.style.cursor = cursor_in_line(cursor_data, line, this);
                    return true;
                }
                else if (editor.paintForeground === undefined || editor.paintForeground == null){
                    this.off("mousedown");
                }
            }
            else { this.off("mousedown"); }
            
        }
        editor.style.cursor = undefined;
        return true;

        function set_resize_cursor(evt, rects) {
            let cursor_chenge = {resize:false, index: 0}
            //let cursor_chenge = 0;
            let x = evt.clientX - editor.offsetLeft;
            let y = evt.clientY - editor.offsetTop;
            for (let i = 0; i < rects.length; i++){
                if ((x > rects[i].x1) && (x < rects[i].x2) &&
                    (y > rects[i].y1) && (y < rects[i].y2)){
                        cursor_chenge = {resize:true, index: i + 1};
                    break;
                }
                else 
                {
                    cursor_chenge = {resize:false, index: i + 1};
                }
            }
            return cursor_chenge;
        }

        function cursor_in_line(_cursor_data, line, container) {
            container.off("mousedown");
            let cursor = undefined;
            let index = _cursor_data.index;
            if(_cursor_data.resize)
            {
                if (index % 2 == 0) { cursor = "ns-resize"; }
                else { cursor = "ew-resize"; }
            }
            else { cursor = "pointer"; }
            
            container.on("mousedown", (e)=> {if(_cursor_data.resize) mousedown(e); else container.off("mousedown")/*line.SetSelect(container);*/} );
            return cursor;

            function mousedown(e){
                container.on("mouseup", mouseup);
                let mouse_down = false;
                if (e.buttons === 1) { setTimeout(runEvent, 100);}//runEvent() }
                

                function runEvent(){
                    if (!mouse_down ) { line.doDrag_line(evt.target, e, index, line, container); }
                    
                    else { line.SetSelect(container); }
                    container.off("mousedown");
                }

                function mouseup(evt){
                    mouse_down = true;
                    GetEditorApp().off('mousemove')
                    container.off("mousedown")
                    container.off("mouseup")
                }
            }

        }
        
    }

    DeleteLines(del_lines){
        let cmd_undo = [];
        let container = this;
        let line_set = container.lines.filter(filter_callback)

        container.lines = line_set;

        container.componentUpdate();
        return cmd_undo;

        function filter_callback(value, index, arr){
            let res = true;
            for (let line of del_lines){
                if(line.getAttribute("id") == index){
                    cmd_undo.push({command: Connectors._AddConnector , parameters: {this: container, lines: "lines", line: value} })
                    res = false;
                    break;
                }
            }
            return res;
        }
    }

    DeleteLinesFromElements(elements, cmd_undo){
        let container = this;
        let line_set = container.lines.filter(filter_callback)
        container.lines = line_set;
        container.componentUpdate();
        return cmd_undo;

        function filter_callback(value, index, arr){
            let res = true;
            for(let el of elements){
                if (el.constructor.name != "Plc"){
                    let el_name = el.getAttribute("id");
                    if(value.first_target.target == el_name || value.second_target.target == el_name){
                        cmd_undo.push({command: Connectors._AddConnector , parameters: {this: container, lines: "lines", line: value} })
                        res = false;
                        break;
                    }
                }
            }
            return res;
        }
    }

    EventMouseOut(container, evt)
    {
        let editor = GetEditorApp();
        if(!editor.read_only) {
            if (editor.paintForeground === undefined || editor.paintForeground == null){
                //let editor = document.$("#editor_app");
                editor.style.cursor = undefined;
                container.off("mousemove");
            }
        }
    }

    EventMouseOver(container, evt)
    {
        let editor = GetEditorApp();
        if(!editor.read_only) {
            if (editor.paintForeground === undefined || editor.paintForeground == null){
                for (let line of container.lines) { line.set_rects_line(); }
                    container.on("mousemove", function(e) { container.onmove_line(e, container.lines, editor) ;});
            }
            return true;
        }
    }

    EventMouseClick(container, evt)
    {
        let editor = GetEditorApp();
        for (let line of container.lines){
            if (cursorInPath(evt, line.GetStartEndPath()))
            {
                line.SetSelect(container);
                return true;
            }
        }
        return false;

        function cursorInPath(e, rects) {
            let x = e.clientX - editor.offsetLeft;
            let y = e.clientY - editor.offsetTop;
            for (let i = 0; i < rects.length; i++){
                if ((x > rects[i].x1) && (x < rects[i].x2) &&
                    (y > rects[i].y1) && (y < rects[i].y2)){
                        return true;
                }
            }
            return false;
        }
    }

    //["on mouseout"](evt) { this.EventMouseOut(this, evt); }

    //['on mouseover'](evt) { this.EventMouseOver(this, evt); }

    onmouseout(evt) { if(evt.buttons !== 4) GetEditorApp()?.EventsManager.pushEvent({container: this, callback: this.EventMouseOut, args:evt, flag: GetEditorApp().evt_flag}); }

    onmouseover(evt) { if(evt.buttons !== 4) GetEditorApp()?.EventsManager.pushEvent({container: this, callback: this.EventMouseOver, args:evt, flag: GetEditorApp().evt_flag}); }
    //onmousedown(evt) { this.EventsManager.pushEvent( {container: this, callback: this.MouseDown, args: evt, flag: GetEditorApp().evt_flag}); }
    onmousedown(evt) { GetEditorApp()?.EventsManager.pushEvent({container: GetEditorApp(), callback: GetEditorApp()?.MouseDown, args: evt, flag: GetEditorApp().evt_flag}); }

    onclick(evt) { GetEditorApp()?.EventsManager.pushEvent({container: this, callback: this.EventMouseClick, args: evt, flag: GetEditorApp().evt_flag}); }

    isConnected(target, ch)
    {
        let res = false;
        for (let line of this.lines)
        {

            let targets = [line.first_target.target, line.second_target.target]
            let ch_list = [line.first_target.ch, line.second_target.ch]

            if ( targets.includes(target) )
            {
                if( ch_list.includes(ch))
                {
                    res = true;
                    break;
                }
                
            }
        }
        return res;
    }

    render(props) {
        this.viewBox = {x: Number.MAX_SAFE_INTEGER, y: Number.MAX_SAFE_INTEGER, x_max: 0, y_max: 0};
        let lines_render = new Array
        for (let i = 0; i < this.lines.length; i++){
            this.lines[i].id_name = i;
            let rectbox         = this.lines[i].get_rectbox();
            this.viewBox.x      = Math.min(rectbox.x, this.viewBox.x);
            this.viewBox.y      = Math.min(rectbox.y, this.viewBox.y);
            this.viewBox.x_max  = Math.max(rectbox.max_x, this.viewBox.x_max);
            this.viewBox.y_max  = Math.max(rectbox.max_y, this.viewBox.y_max);
            lines_render.push(this.lines[i].render());
        }

        let left = this.viewBox.x;
        let width = this.viewBox.x_max - this.viewBox.x;

        let top = this.viewBox.y;
        let height = this.viewBox.y_max - this.viewBox.y;

        return <svg xmlns="http://www.w3.org/2000/svg" 
                    id="connectorLines"
                    viewBox={`${this.viewBox.x} ${this.viewBox.y} ${this.viewBox.x_max - this.viewBox.x} ${this.viewBox.y_max - this.viewBox.y}`}
                    width={width} height={height} 
                    style={`left: ${left}px; top: ${top}px;`}>
                        {lines_render}
               </svg>
    }
}