import { round5 } from "../round";
import { get_zoom, zoom_array } from "./editor";
import { ElementConnector } from "ElementConnector";



export function _get_pos_connector(connector, left, top){
    let zoom = get_zoom();
    var [x,y,width, height] = connector.state.box("xywh", "margin", "container");
    let move_x = (connector.offsetLeft + (width / 2)) / zoom;
    let move_y = (connector.offsetTop + (height / 2)) / zoom;
    return [move_x + left, move_y + top]
}

function GetEditorApp(body_tree) { return document.$("#editor_app"); }

export class SimElement extends Element
{
    constructor(props, kids, parent)
    {
        super();
        this.editor = (typeof(props.editor) === "object") ?  props.editor : this.closest("editor");
        this.target = props.target;
        this.kids = kids;
        this.top = (props.y) ? round5(props.y) : 0;
        this.left = (props.x) ? round5(props.x) : 0;
        this.props = props;
        this.height = props.height;
        this.width = props.width;
        this.target_name = props.tagname;
        this.connectors = new Array();
        this.attrs = (props.attrs) ? props.attrs : new Array();
        this.lines_path = new Array();
        this.undo = new Array();
        this.redo = new Array();
        this.image = new Array();
        for (let i = 0; i < zoom_array.length; i++)
        {
            this.image[i] = null;
        }
        this.old_zoom = 1;
    }

    set_connectors(pins)
    {
        for (let pin of pins){
            this.connectors.push( <ElementConnector target={this.target}
                                      index={pin.index} 
                                      id_name={`${pin.name}`} 
                                      x={pin.x} 
                                      y={pin.y} 
                                      interface={pin.type}>
                                  </ElementConnector> )
        }
    }

    get_target(){
        return this.target_name;
    }

    push_line(line, pin){
        let data = line.get_storage()
        if (data.second_target.ch && data.second_target.target){
            document.$("#editor_app").storage.connectors.push(data);
        }
        this.lines_path.push({line: line, connector: pin});
    }
    get_paths(){
        let lines_data = [];
        for (let line of this.lines_path ) {
            lines_data.push( line.line.get_storage() );
        }
        return lines_data;
    }

    getDragPointer(x, y) {
        const elRect = this.getBoundingClientRect();
        this.shiftX = elRect.left;
        this.shiftY = elRect.top;
    }

    get_storage(){
        return {type: this.constructor.name, tagname: this.target_name, y: this.top, x: this.left, height: this.height, width: this.width, attrs: this.attrs}
    }

    prepareElement() {
        this.style.position = "absolute";
        this.style.zIndex = 999;
    }

    set_output_callback(this_out_ch, callback) {
        let connector = this.$(`#${this_out_ch}`);
        connector.set_callback(callback);
    }

    get_callback(this_in_ch){
        let connector = this.$(`#${this_in_ch}`)
        return connector.get_callback()
    }

    move(x, y){
        if(!isNaN(x + y)){
            this.left += x;
            this.top  += y;
            this.editor.componentUpdate();
            this.connector_move(this.left + 5, this.top + 5);
            return true
        }
        else {
            console.error("Move positions is NaN!");
            return false;
        }
    }

    get_style(){
        let x = round5(this.left);
        let y = round5(this.top);
        return `left: ${x}; top: ${y};`;
    }

    connector_move(el_left, el_top){
        for (let line of this.editor.get_connectors().lines){
            if (this.target_name === line.first_target.target){
                let el = this.editor.$(`#${line.first_target.ch}`);
                if(el){
                    let [x, y] = _get_pos_connector(this.$(`#${line.first_target.ch}`), el_left, el_top);
                    line.move_first_target(x, y)
                }
            }
            if (this.target_name === line.second_target.target){
                let el = this.editor.$(`#${line.second_target.ch}`);
                if( el ) {
                    let [x, y] = _get_pos_connector(el, el_left, el_top);
                    line.move_second_target(x, y)
                }
            }
        }
    }

    isReadOnly() { return this.editor.read_only; }

    _set_image(i) { 
        if(typeof(i) === "number") { 
            delete this.image[i];
            //this.image[i] = new Graphics.Image(this); 
            // rectangle: m 0 0 H 100 V 100 H 0 V 0
            this.image[i] = new Graphics.Path(`m 0 0 H ${this.width * zoom_array[i]} V ${this.height * zoom_array[i]} H 0 V 0`);
            //gc();
        } 
    }

    SetImageData(zoom)
    {
        let i = zoom_array.indexOf(zoom)
        if(typeof(i) === "number"){
            if(this.image[i] === null) { 
                this._set_image(i);
            }
        }
    }

    GetDrawData(zoom)
    {
        let i = zoom_array.indexOf(zoom)
        if(typeof(i) === "number")
        {
            this.SetImageData(zoom);
            let x = ( Number(this.style.left) + Number(this.style.marginLeft) );
            let y = ( Number(this.style.top) + Number(this.style.marginTop) );
            
            return{x: x, y: y, image: this.image[i]}
        }
        return undefined;
    }

    settingsIsValid(attrs)
    {
        return null;
    }

    element_settings(){
        if ( !this.isReadOnly() ){
            if (this.settings){            
                var wnd = Window.this.modal({
                    url   : __DIR__ + "settings/element-settings.htm", 
                    state : Window.WINDOW_SHOWN,
                    parameters: {settings: this.settings, set_settings: this.attrs}
                });

                let error = this.settingsIsValid(wnd)
                
                if(error === null){
                    if(wnd)
                    {
                        this.attrs = wnd;
                        return true;
                    }
                    
                }
                else{
                    const err_head = @"Error" + ". " + @"Parameters not set. "
                    var r = Window.this.modal(<error><p>{err_head}</p>
                                         <p> {error} </p></error>);
                }
            }
        }
        return false;
    }

    /** Events */
    EventMouseDtagRequest(container, evt) {
        if ( !container.isReadOnly() ) {
            if (container.editor.paintForeground === undefined || container.editor.paintForeground == null){
                if (evt.buttons != 4) {
                    if (container.attributes["selected"]) {
                        container.editor.drag_selection(evt, container)
                        container.componentUpdate();
                        return true;
                    }
                    else {
                        container.editor.clearSelection(".draggable");
                        container.attributes["selected"] = true;
                        container.editor.drag_selection(evt, container)
                        container.componentUpdate();
                        return true;
                    }
                }
                else {
                    return container.editor.pagescroll(container.editor, evt);
                }
            }
        }else {
            if(container.MouseDragRequest) {
                container.MouseDragRequest(evt);
                container.change_element_in_event();
            }
        }
    }

    EventWheel(container, evt) {
        if (container.isReadOnly()) {
            if(container.Wheel) {
                container.Wheel(evt);
                container.change_element_in_event();
            }
        }
    }

    EventDblCkick(container, evt) {
        if(!container.isReadOnly()) {
            container.element_settings();
        }
        else {
            if(container.DblClick){
                container.DblClick(evt);
                container.change_element_in_event();
            }
        }
    }

    EventClick(container, evt)
    {
        if ( !container.isReadOnly() ){
            if (evt.buttons !== 4){
                if (evt.ctrlKey) {
                    if (container.attributes["selected"] == undefined) {
                        container.attributes["selected"] = true;
                    }
                    else {
                        container.attributes["selected"] = undefined;
                    }
                    return true;
                }
                else{
                    container.editor.clearSelection(".draggable");
                    container.attributes["selected"] = true;
                }
            }
        }else{
            if(container.Click){
                container.Click(evt);
                container.change_element_in_event();
            }
        }
    }

    EventMouseDown(container, evt)
    {
        if ( container.isReadOnly() ){
            if(container.MouseDown){
                container.MouseDown(evt);
                container.change_element_in_event();
            }
        }
        
    }

    EventMouseUp(container, evt)
    {
        if ( container.isReadOnly() ){
            if(container.MouseUp){
                container.MouseUp(evt);
                container.change_element_in_event();
            }
        }
    }

    onmousedragrequest(evt) { this.editor.EventsManager.pushEvent({container: this, callback: this.EventMouseDtagRequest, args: evt, flag: this.editor.evt_flag}); }

    change_element_in_event()
    {
            this.componentUpdate();
            //let i = zoom_array.indexOf(zoom)
            //setTimeout(this._set_image, 200, i);
    }
    onwheel(evt){ this.editor.EventsManager.pushEvent( {container: this, callback: this.EventWheel, args: evt, flag: this.editor.evt_flag}); }

    ondblclick(evt) { this.editor.EventsManager.pushEvent({container: this, callback: this.EventDblCkick, args:evt, flag: this.editor.evt_flag}); }

    onclick(evt) { this.editor.EventsManager.pushEvent({container: this, callback: this.EventClick, args: evt, flag: this.editor.evt_flag }); }

    /*onclick(evt) {
        this.EventClick(this, evt); 
    }*/

    onmouseup(evt){ this.editor.EventsManager.pushEvent({container: this, callback: this.EventMouseUp, args: evt, flag: this.editor.evt_flag }); }
    
    
    onmousedown(evt) {
        if(evt.buttons === 4){ this.editor.EventsManager.pushEvent({container: this.editor, callback: this.editor.pagescroll, args: evt, flag: this.editor.evt_flag }); }
        
        else { this.editor.EventsManager.pushEvent({container: this, callback: this.EventMouseDown, args: evt, flag: this.editor.evt_flag }); }
    }

    UpdateAllConnectors()
    {
        for(let connector of this.$$("div.connector") )
        {
            connector.set_out_last_value();
        }
    }
}

