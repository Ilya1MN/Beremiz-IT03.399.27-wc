import { Connectors } from "./connector";
import { round5 } from "../round";
import { Stack } from "../types";

export const zoom_array = [1, 2, 4, 5]
const undo_redo_sz = 50;

function GetAllElements(doc)
{
    return doc.$$(".draggable")
} 
    

export function get_zoom(){ return document.body.style.zoom; }

class KeydownEvent{
    constructor(){
        this._event_list = []
    }

    add_event(key_code, callback){
        this._event_list.push({key_code: key_code, callback: callback})
    }

    remove_event(){
        this._event_list.pop();
    }

    get_events(){
        return this._event_list;
    }
}

class EventManager{
    
    constructor()
    {
        this._flag = false;
    }
    pushEvent(event_obj)
    {
        if(!event_obj._flag)// && Window.this.isTopmost && Window.this.isOnActiveSpace && Window.this.isEnabled && Window.this.isAlive)
        {
            event_obj._flag = true;
            event_obj.callback(event_obj.container, event_obj.args);
            event_obj._flag = false;
        }
    }
}


class Editor extends Element
{
    default_storage = { version: 1,
                        autor: "",
                        editor_position: {x: 0, y: 0},
                        elements: [],
                        connectors: [] };

    constructor(props, kids) {
        super();
        this.EventsManager = new EventManager();
        this.keys_event = new KeydownEvent();
        this.plc_name = props.target;
        this.logger = props.logger;
        this.storage = (props.storage) ? props.storage : this.default_storage;

        this.zoom_index = 0;

        this.elements = kids;
        this.dragg = false;
        this.connectors = new Array();
        
        this.undo = new Stack(undo_redo_sz);
        this.redo = new Stack(undo_redo_sz);
        this.projectName = props.projectName;
        this.path_project = props.path;
        this.read_only = false;
        this.left = this.storage.editor_position.x;
        this.top = this.storage.editor_position.y;
        this.init = true;
        this.evt_flag = false;
        if (props.storage){
            this.connectors_storage = props.storage.connectors;
            this.set_storage(props.storage);
        }
        else {
            this.load_new_file();
        }

    }
        /*if (globalThis["MbrtuStatusClass"]) { 
            this.MbrtuStatus = globalThis["MbrtuStatusClass"]; 
            this.MbrtuStatus.setEditorFlag(true);
        }

        else { this.MbrtuStatus = undefined; }
        //console.log(this.MbrtuStatus);
    }

    //destructor
    oncloserequest(evt)
    {
        console.log("close editor");
        this.MbrtuStatus.setEditorFlag(false);
    }*/

    disableEvents()
    {
        if(!this.evt_flag) { 
            this.evt_flag = true; 
            return true;
        }
        return false;
    }
    enableEvents()
    {
        if(this.evt_flag) { 
            this.evt_flag = false
            return true;
        }
        return false;
    }

    get_target_name(){
        return this.plc_name;
    }

    set_read_only(state){
        if(state) { this.InitAllElements(); }
        this.read_only = state
    }

    InitAllElements()
    {
        for( let element of GetAllElements(this) )
        {
            element.UpdateAllConnectors();
        }
        
    }

    get_project_path(){
        return this.path_project;
    }

    get_connectors() {
        return this.$("svg#connectorLines");
    }

    load_new_file(){
        this.load_plc();
    }

    load_plc(){
        this.elements.push(globalThis["Plc"]({  tagname: this.plc_name,
                                            x: 10,
                                            y: 10,
                                            editor: this,
                                        }));
    }

    set_storage(storage){
        let load_connectors = true;
        if (storage.elements){
            if (storage.elements.length){
                for(let element of storage.elements ){
                    let attrs = {tagname: element.tagname, x: element.x, y: element.y, height: element.height, width: element.width, editor: this, attrs: element.attrs}
                    let el = globalThis[element.type](attrs)
                    this.elements.push(el)
                }
            }
            else {  this.load_plc(); load_connectors = false; }
        }
        else {  this.load_plc(); load_connectors = false; }

        return true;
    }

    get_storage(){
        let elements = [];//{};
        let lines = [];
        for(let element of GetAllElements(this)){
            elements.push(element.get_storage());
        }

        for (let line of this.get_connectors().lines){
            lines.push(line.get_storage());
        }


        let storage = { 
                        version: 1,
                        autor: "TestName",
                        editor_position: {x: this.left, y: this.top},
                        elements: elements,
                        connectors: lines
                    }
        return storage;
    }

    get_save_storage(){
        
    }

    clearSelection(selector) {
        let select_elements = this.getSelections(selector)
        for( var el of select_elements ) {
            el.attributes["selected"] = undefined;
        }
    }

    getSelections(selector){
        return this.$$(`${selector}[selected]`);
    }

    get_targetname(target_name){
        let name = target_name + Math.floor(Math.random() * 1000);
        if(document.getElementById(name) !== null){
            return this.get_targetname(target_name)
        }
        else {
            return name;
        }
    }

    AppendKids(elements, attrs){
        
        this.elements.push(elements);
        this.storage.elements.push({type: attrs.type, tagname: attrs.tagname, x: attrs.x, y: attrs.y})
        this.componentUpdate();
    }

    static DeleteElement(params){
        if(params.this && params.elements && params.this[params.elements].length > 1){
            let el = params.this[params.elements].pop();            
            return {command: Editor.AddElement , parameters: {this: params.this, elements: params.elements, el: el} }
        }
    }

    static AddElement(params){
        if (params.this && params.elements && params.el){
            params.this[params.elements].push(params.el); 
            return {command: Editor.DeleteElement, parameters: {this: params.this, elements: params.elements}};
        }
    }

    AppendKidFromLib(target_name, left, top, module_src){
        left = round5(left - this.offsetLeft) / get_zoom() - this.left;
        top = round5(top - this.offsetLeft) / get_zoom() - this.top;
        let el_target_name = this.get_targetname(target_name);
        let attrs = {type: target_name,tagname: el_target_name, x: left, y: top, height: 30, width: 50, editor: this}
        let element = globalThis[target_name](attrs);
        this.AppendKids(element, attrs);
        this.undo.push([{command: Editor.DeleteElement, parameters: {this: this, elements: "elements"}}])
    }

    render() {
        
        let elements = this.$$(".draggable");
        let lines = this.$$(".line_path");
        for(let el of elements){

            if (el?.style?.visibility){ el.style.visibility = undefined; }
            /*if(el.SetImageData)
            {
                if(this.init) { for(let zoom of zoom_array) { el.SetImageData(zoom); }}
                else { el.SetImageData(get_zoom()); }
            }*/
        }
        if(this.init) { 
            this.init = false; 
            
            //this.InitComponents();
            
        }

        for (let line of lines) { if (line?.style?.visibility){ line.style.visibility = undefined; } }

        return (<div id="editor_app">
                    <div id="editor" style={`left: ${this.left}; top: ${this.top};`}>
                        {this.elements}
                        <Connectors storage={this.connectors_storage} left={this.left} top={this.top}/>
                    </div>
                </div>)
    }

    IsChange()
    {
        if (this.get_storage() === this.get_save_storage() ) {return true;}
        else return false
    }

    Redo(){
        if (this.redo.length){
            let redo = this.redo.pop();
            let undo = [];
            for(let cmd of redo){
                if (cmd.command) {
                    let undo_cmd = cmd.command(cmd.parameters)
                    if(undo_cmd) {
                        undo.push(undo_cmd);
                    }
                }
                else {
                    console.error("Redo command not found!!!");
                }
            }
            if (undo.length > 0){
                this.undo.push(undo);
            }
            this.componentUpdate();
        }
    }

    Undo() {
        if (this.undo.length){
            let undo = this.undo.pop()
            let redo = []
            for(let cmd of undo) {
                if (cmd.command) {
                    let redo_cmd = cmd.command(cmd.parameters)
                    if (redo_cmd) {
                        redo.push(redo_cmd);
                    }
                }
                else {
                    console.error("Undo command not found!!!");
                }
            }
            if (redo.length > 0){
                this.redo.push(redo)
            }
            this.componentUpdate();
        }
    }

    set_settings()
    {
        let elements = this.getSelections(".draggable")
        for (let element of elements) {
            if (element.constructor.name == "Plc"){
                element.set_settings();
                return;
            }
        }
    }

    DeleteElements(elements){
        if(Array.isArray(elements)){
            let cmd_undo = [];
            let container = this;
            let elements_set = container.elements.filter(filter_callback)
            container.elements = elements_set;
            let connectors = container.get_connectors();
            cmd_undo = connectors.DeleteLinesFromElements(elements, cmd_undo)
            container.componentUpdate();
            return cmd_undo;

            function filter_callback(value, index, arr){
                for (let element of elements) {
                    if (element.constructor.name != "Plc"){
                        if(value[1].tagname.search(element.getAttribute("id")) != -1){
                            cmd_undo.push({command: Editor.AddElement , parameters: {this: container, elements: "elements", el: value} })
                            container.$("#editor").removeChild(element);
                            return false;
                        }
                    }
                }
                return true;
            }
        }
    }

    DeleteLines(lines){
        let cmd_undo = []
        let container = this.get_connectors();
        cmd_undo = container.DeleteLines(lines)
        return cmd_undo;
    }

    output_to_input_connectors_init(el_connectors){
        for(let connection of el_connectors){
            let element_out = this.$(`#${connection.output.target}`);
            let element_in = this.$(`#${connection.input.target}`);
            let connector_out = connection.output.ch;
            let connector_in = connection.input.ch;

            let callback = element_in.get_callback(connector_in);
            element_out.set_output_callback(connector_out, callback);
        }
    }

    init_run_emulator(){
        this.clear_interfaces();
        let lines = this.get_storage().connectors;
        let work_interf = [];
        for (let line of lines){
            let parce_line = {input: undefined, output: undefined};
            set_i_o_obj(line.first_target, parce_line);
            set_i_o_obj(line.second_target, parce_line);
            if (parce_line.input && parce_line.output){
                work_interf.push(parce_line);
            }
        }

        this.output_to_input_connectors_init(work_interf)

        function set_i_o_obj(target, param){
            if(target.direction === "input"){
                param.input = target;
            }
            else if (target.direction === "output"){
                param.output = target;
            }
        }
    }

    clear_interfaces(){
        let elements = this.$$(".draggable");
        for(let element of elements){
            for(let connector of element.$$(".connector")){
                connector.clear_output_interface();
            }
        }
    }

    /** Events */

    EnableAllEvents()
    {
        //let editor = document.$("#editor_app")
        this.addEventListener("mousedragrequest", this.mouseDragRequest);
        this.addEventListener("mousedown", this.MouseDown);
    }

    DisableAllEvents()
    {
        //let editor = document.$("#editor_app")
        this.removeEventListener("mousedragrequest", this.mouseDragRequest);
        this.removeEventListener("mousedown", this.MouseDown);
    }

    mouseDragRequest(container, evt)
    {
        if (!container.read_only)
        {
            if (container.paintForeground === undefined || container.paintForeground == null){
                return container.RectangleSelector(evt);
            }
        }
    }
    
    grag_selected_update(el_selected){
        this.get_connectors().componentUpdate();
        this.componentUpdate();
    }

    drag_selection(evt, element)
    {
        var cx, cy;
        
        let svg_connectors = this.get_connectors()
        let zoom = this.parentNode.style.zoom
        var ax = ((evt.clientX - this.offsetLeft) / zoom);
        var ay = ((evt.clientY - this.offsetTop) / zoom);

        var selected = this.getSelections(".draggable");

        var selected_lines = this.getSelections(".line_path");

        if (selected.length === 0 && selected_lines.length === 0)
        {
            element.attributes["selected"] = true;
            element.componentUpdate();
            selected = this.getSelections(".draggable");
        }

        function onmove(evt) {
            cx = ((evt.clientX - this.offsetLeft) / zoom);
            cy = ((evt.clientY - this.offsetTop) / zoom);
            this.requestPaint();
        }

        this.post(function () {
            var images = {elements: new Array(), lines: new Array()};
            const MARGIN = 5;
            for(let el of selected) { 
                var x = (Number(el.style.left) + MARGIN) * zoom;
                var y = (Number(el.style.top) + MARGIN) * zoom;
                images.elements.push({image: new Graphics.Image(el), x: x, y: y});
                el.style.visibility = "hidden";
                el.attributes["dnd"] = ""; 
            }

            for(let line_dom of selected_lines){
                let index = line_dom.getAttribute("id")
                let line = svg_connectors.lines[index]
                if(line){
                    let d = line.get_attribute_d(zoom);
                    line_dom.style.visibility = "hidden";
                    images.lines.push({image: new Graphics.Path(d), x: 0, y: 0});
                }
            }
            //gc();

            this.paintForeground = function(gfx){
                for ( let image of images.elements) {
                    gfx.draw(image.image, {x: round5((image.x + (this.left + cx - ax)*zoom)), y: round5((image.y + ( this.top + cy - ay)* zoom))});
                }
                for( let image of images.lines){
                    gfx.lineWidth = 2;
                    gfx.strokeStyle = Color.RGB(148,148,148);
                    gfx.fillStyle = Color.RGB(148,148,148, 50);
                    gfx.draw(image.image, {x: round5((image.x + (this.left + cx - ax)*zoom)), y: round5((image.y + ( this.top + cy - ay)* zoom)),  stroke: true});
                }
            };

            // 2. short circuit mouse moves to document
            this.state.capture(true);
            this.on("mousemove", onmove);

            // 3. run "mouse modal loop" until mouse depressed
            let r = Window.this.doEvent("untilMouseUp");
            // 4. return things back
            this.state.capture(false);
            this.off(onmove);
            this.paintForeground = undefined;
            this.requestPaint();
            let selected_id = []
            for(let el of selected){
                selected_id.push(el.getAttribute("id"));
            }
            let set_pos_el = {sel: selected_id, move_method: "move", x: (cx - ax)/* - 5*/, y: (cy - ay)/* - 5*/}            
            
            

            let line_param = {sel: selected_lines, path: svg_connectors.lines, x: (cx - ax), y: (cy - ay)}
            
            

            this.undo.push([set_position(set_pos_el), set_position_lines(line_param)]);
            this.storage = this.get_storage();
            this.clearSelection(".line_path")
            this.grag_selected_update(selected);
            
            function set_position_lines(param){
                for (let line of param.sel) {
                    let index = line.getAttribute("id")
                    if(!isNaN(param.x + param.y)){
                        for (let i = 0; i < param.path[index].lines.length - 2; i++ ){
                            let set_val = (i % 2 == 0) ? param.x : param.y;
                            param.path[index].lines[i] = (param.path[index].lines[i] + set_val);
                            //param.path[index].lines[i] += (i % 2 == 0) ? param.x : param.y;
                        }
                    }
                    else {
                        console.error("Move positions is NaN!");
                    }
                }
                return {command: set_position_lines, parameters: {sel: param.sel, path: param.path, x: -param.x, y: -param.y}}
            }

            function set_position(param){ 
                let editor = document.$("#editor_app")   
                
                if(param.sel && param.move_method && param.x && param.y){
                    let round_x = (param.x % 5) ? round5(param.x) : param.x;
                    let round_y = (param.y % 5) ? round5(param.y) : param.y;
                    for(let id of param.sel) { 
                        let el = editor.$(`#${id}`)
                        if(el){
                            if(el.attributes){
                                el.attributes["dnd"] = undefined;
                            }
                            
                            if( el[param.move_method] ) {
                                el[param.move_method](round_x, round_y);
                            }
                        }
                        //if (el.style) { el.style.visibility = undefined; }
                    }
                    return {command: set_position, parameters: {sel: param.sel, move_method: param.move_method, x: -round_x/* - 5*/, y: -round_y/* - 5*/}}
                }
            }
        });
        
    }

    Zoom(evt){
        if(evt.deltaY < 0){
            if(this.zoom_index < zoom_array.length - 1){
                this.zoom_index = this.zoom_index + 1;
                let zoom = zoom_array[this.zoom_index]
                document.body.style.zoom = zoom;
                //this.left += -((evt.clientX) * (zoom - oldzoom));
                //this.top += -((evt.clientY) * (zoom - oldzoom));
                //document.scrollBy((evt.clientX / 2) * zoom, (evt.clientY / 2) * zoom);
            }
        }
        else{
            if(this.zoom_index != 0) {
                this.zoom_index = this.zoom_index - 1;
                let zoom = zoom_array[this.zoom_index]
                document.body.style.zoom = zoom;
                //this.left += -((evt.clientX) * (zoom - oldzoom));
                //this.top += -((evt.clientY) * (zoom - oldzoom));
                //document.scrollBy(-(evt.clientX) * zoom, -(evt.clientY) * zoom);
            }
            
        }
        //document.body.componentUpdate();
        return true;

        function setzoom(z) {
            var zoom = (document.body.style.zoom) ? document.body.style.zoom : 1;
            if (z) { zoom = zoom + .2; }
            else { zoom = zoom - .2; }
          
            if (zoom <= 0.4) zoom = 0.4;
            else if (zoom >= 4) zoom = 4;
            document.body.style.zoom = zoom;
        }
    }

    MouseUp(evt){
        
        var container = this;
        if (evt.target === container)
        {
            container.clearSelection(".draggable");
            container.clearSelection(".line_path");
            this.get_connectors().componentUpdate();
        }
        
        return true;
    }

    RectangleSelector(evt){
        var ax, ay;
        var cx, cy;
        var container = this;
        let lines_container = container.get_connectors()
        for (let line of lines_container.lines) { line.set_rects_line(); }
        doDrag(this, evt);
        return true;

        function doDrag(element, e) {
            var _draggble = false;
            function onmove(e) {
                if (!_draggble) {
                    
                    ax = e.clientX - container.offsetLeft;
                    ay = e.clientY - container.offsetTop; //Set the initial Y
                    container.paintForeground = drawCover;
                    _draggble = true;
                }
                else {
                    cx = e.clientX - container.offsetLeft; //Update the current position X
                    cy = e.clientY - container.offsetTop; //Update the current position Y
                    container.requestPaint();
                    onCoverChanged(".draggable");
                    onCoverChanged(".line_path")
                }
                
            }

            element.post(function () {
                // 1. short circuit mouse moves to document 
                element.state.capture(true);
                element.on("mousemove", onmove);
                // 2. run "mouse modal loop" until mouse depressed
                let r = Window.this.doEvent("untilMouseUp");
                // 3. return things back
                container.paintForeground = undefined;
                container.requestPaint();
                element.state.capture(false);
                element.off(onmove);
            });
        }

        function drawCover(gfx) {
            gfx.fillStyle = Color.RGB(148,148,148, 50);
            gfx.strokeStyle = Color.RGB(148,148,148);
            gfx.lineWidth = 1;
            gfx.beginPath()
            gfx.rect(ax, ay, cx - ax, cy - ay)
            gfx.stroke();

            gfx.fill();
            gfx.closePath();
            return true;
          }
        
        function onCoverChanged(selector) {
            if (selector === ".line_path"){ return onCoverChangedLines()}
            var x1 = Math.min(ax, cx), x2 = Math.max(ax, cx); 
            var y1 = Math.min(ay, cy), y2 = Math.max(ay, cy); 
            var childs = container.$$(selector);
                for (var ch of childs ) {
                    var [cx1,cy1,cx2,cy2] = ch.state.box("rect", "border", "document")
                    cx1 -= container.offsetLeft;
                    cx2 -= container.offsetLeft;
                    cy1 -= container.offsetTop;
                    cy2 -= container.offsetTop;
                    ch.attributes["selected"] = ( Math.max(x1,cx1) < Math.min(x2,cx2) && Math.max(y1,cy1) < Math.min(y2,cy2) )? true : undefined;
                }
        }

        function onCoverChangedLines(){
            let x1 = Math.min(ax, cx), x2 = Math.max(ax, cx); 
            let y1 = Math.min(ay, cy), y2 = Math.max(ay, cy); 

            let containerLines = document.body.$("#connectorLines")
            let lines = containerLines.lines;
            for ( let i = 0; i < lines.length; i++ ){
                let selected = undefined;
                let line_rects = [...lines[i].rects_path_start, ...lines[i].rects_path, ...lines[i].rect_path_end]
                for(let rect of line_rects){
                    selected = ( Math.max(x1, rect.x1) < Math.min(x2, rect.x2) && Math.max(y1, rect.y1) < Math.min(y2, rect.y2) ) ? true : undefined;
                    if( selected ){
                        break;
                    } 
                }
                containerLines.$(`#${i}`).attributes["selected"] = selected
            }
        }
    }

    pagescroll(container, evt){
        let zoom = get_zoom();
        
        let ax = evt.clientX - container.offsetLeft;
        let ay = evt.clientY - container.offsetTop;
        let cx = ax;
        let cy = ay;
        let draw = false;

        let all_el_in_editor = container.$$(".draggable");//[...this.$$(".draggable"), ...this.$$(".line_path")]
        let svg_connectors = container.get_connectors()
        let all_line_in_editor = svg_connectors.lines;
        let images = {elements: new Array(), lines: new Array()};
        
        document.post(function () {
            container.addEventListener("mouseup", mouseup);
            document.addEventListener("mouseout", mouseout);
            container.addEventListener("mousemove", onmove);
        });

        function set_images(){
            for( let el of all_el_in_editor ){
                let draw_data = el.GetDrawData(zoom)
                if(draw_data) { images.elements.push({image: draw_data.image, x: draw_data.x * zoom, y: draw_data.y * zoom}); }
                el.style.visibility = "hidden";
                /*var x = ( Number(el.style.left) + Number(el.style.marginLeft) ) * zoom;
                var y = ( Number(el.style.top) + Number(el.style.marginTop) ) * zoom;
                if (!isNaN(x + y)){
                    images.elements.push({image: new Graphics.Image(el), x: x, y: y});
                    el.style.visibility = "hidden";
                }*/
            }

            /*for (let line of all_line_in_editor){
                let d = line.get_attribute_d(zoom);
                set_hidden(line.id_name);
                images.lines.push({image: new Graphics.Path(d), x: 0, y: 0});
            }*/

            for (let line of all_line_in_editor){
                set_hidden(line.id_name);
                images.lines.push({image: line.GetImage(zoom), x: 0, y: 0});
            }

            function set_hidden(id){
                let line_dom = svg_connectors.$(`#${id}`)
                line_dom.style.visibility = "hidden";
            }
        }

        function draw_editor(gfx){
            
            for ( let image of images.elements) {
                let set_x = (image.x - (ax - cx) + (container.left * zoom))
                let set_y = (image.y - (ay - cy) + (container.top * zoom))
                gfx.lineWidth = 2;
                gfx.strokeStyle = 'rgb(148,148,148)';
                gfx.strokeWidth = 2;
                gfx.font = "-"
                gfx.fillStyle = Color.RGB(148,148,148, 50);
                //gfx.strokeRect(set_x, set_x, 10, 10)
                gfx.draw(image.image, {x: set_x, y: set_y, stroke: true});
            }
            for (let image of images.lines) {
                let set_x = (image.x - (ax - cx) + (container.left * zoom))
                let set_y = (image.y - (ay - cy) + (container.top * zoom))
                gfx.lineWidth = 2;
                gfx.strokeStyle = Color.RGB(148,148,148);
                gfx.fillStyle = Color.RGB(148,148,148, 50);
                gfx.draw(image.image, {x: set_x, y: set_y, stroke: true});
            }
        }

        function onmove(e) {
            if(!draw){ 
                set_images();
                container.paintForeground = draw_editor; 
                draw = true
            }
            else{
                cx = e.clientX - container.offsetLeft;
                cy = e.clientY - container.offsetTop;
                container.requestPaint();
            }
        }

        function mouseup(){
            container.removeEventListener("mousemove", onmove);
            container.removeEventListener("mouseup", mouseup);
            document.removeEventListener("mouseout", mouseout);

            if(!isNaN(ax - cx) && !isNaN(ay - cy)){
                container.left -= (ax - cx) / zoom;
                container.top  -= (ay - cy) / zoom;
            }
            else {
                return false
            }
            container.paintForeground = undefined;
            container.grag_selected_update(all_el_in_editor);
            return true;
        }
        function mouseout(evt){
            if ( !(evt.target.closest("#editor_app")) ) { mouseup(); } 
        }
    }

    MouseDown(container, evt){
        if (!container.read_only){
            if (evt.target.closest("#editor_app") === container){
                if (evt.buttons === 1){
                    container.MouseUp(evt);
                }
            }
        }
        if(evt.buttons === 4){
            if(evt.target.closest("#editor_app") === container){
                container.pagescroll(container, evt)
            }
        }
        return true;
    }

    

    keydown(evt){
        if (!this.read_only)
        {
            if(evt.ctrlKey){
                if(evt.code == "KeyZ"){
                    if(evt.shiftKey){ this.Redo(); }
                    else { this.Undo(); }
                }
            }
            else if(evt.code === "Delete"){
                let elements = this.getSelections(".draggable")
                let lines = this.getSelections(".line_path")
                let cmd_undo_el = [];
                let cmd_undo_line = []
                if (elements){
                    if (elements.length > 0){
                        cmd_undo_el = (this.DeleteElements(elements));
                    }
                }
                if (lines){
                    if (lines.length){
                        cmd_undo_line = ( this.DeleteLines(lines) );
                    }
                }
                let cmd = cmd_undo_el.concat( cmd_undo_line )
                this.undo.push(cmd);
            }

            for (let key_event of this.keys_event.get_events()){
                if(evt.code === key_event.key_code){
                    key_event.callback();
                }
            }
        }
        return true;
    }

    wheel(container, evt) {
        if ( (container.paintForeground === undefined || container.paintForeground == null) && evt.ctrlKey ){
            return container.Zoom(evt)
        }
        else {
            return true;
        }
    }

    onmousedragrequest(evt) { this.EventsManager.pushEvent( {container: this, callback: this.mouseDragRequest, args: evt, flag: this.evt_flag}); }

    onmousedown(evt) { this.EventsManager.pushEvent( {container: this, callback: this.MouseDown, args: evt, flag: this.evt_flag}); }

    onwheel(evt) { this.EventsManager.pushEvent( {container: this, callback: this.wheel, args: evt, flag: this.evt_flag}); }

    /*static InitElementsDraggable(container)
    {
        document.body.componentUpdate()
        let elements = container.$$(".draggable");
        for(let zoom of zoom_array){
            document.body.style.zoom = zoom;
            container.componentUpdate();
            
            for(let el of elements){ 
                el.componentUpdate();
                el.SetImageData(zoom); 
            }
        }
        //if(container.init) { container.init = false; }
        document.body.style.zoom = zoom_array[0];
        container.componentUpdate()
    }*/

    /*static InitComponents()
    {
        let editor = document.body.$("#editor_app")
        editor.componentUpdate();
        Editor.InitElementsDraggable(editor);
    }*/

    /*LoadElementsCache()
    {
        //setTimeout(Editor.InitComponents, 10000);
        //this.InitComponents();
    }*/


}
globalThis["Editor"] = function (attrs) {
    return <Editor storage={attrs.storage} path={attrs.path} projectName={attrs.projectName} target={attrs.target} logger={attrs.logger}></Editor>
};

let editor = document.body.$("#editor_app")
editor.addEventListener("ready", ready);
editor.addEventListener("complete", complete);






