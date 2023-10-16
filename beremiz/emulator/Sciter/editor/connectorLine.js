import { round5, roundX } from "../round";
import { get_zoom } from "./editor";


function GetEditorApp() { return document.$("#editor_app"); }

export class ConnectorLine extends Element
{
    constructor(props, kids){
        //var x = ((props.x) / get_zoom());
        //var y = ((props.y) / get_zoom());
        super();
        this.path_start = `m ${props.x} ${props.y} `
        this.lines = [];
        this.ax = props.x;
        this.ay = props.y;
        this.x = props.x;
        this.y = props.y;
        this.id_name = props.id;
        this.visibility = undefined;
        this.Image = null;
        this.d_attrs = null;

        this.max_x = 0;
        this.max_y = 0;

        this.first_target =  { direction: props.first_direction, ch: props.channel, target: props.target};
        this.second_target = { direction: undefined, ch: undefined, target: undefined };
    }

    set_second_target(target_name, channel, direction){
        if (typeof(target_name) === "string" && typeof(channel) === "string"){
            this.second_target.target = target_name;
            this.second_target.ch     = channel;
            this.second_target.direction = direction;
            return true;
        }
        return false;
    }

    get_target_names_list()
    {
        return [this.first_target.target, this.second_target.target];
    }

    get_attribute_d(zoom){
        let d = `m ${this.ax * zoom} ${this.ay * zoom}`
        for( let i = 0; i < this.lines.length; i++) {
            let path_route = (i % 2 == 0) ? ` H ${this.lines[i] * zoom}` : ` V ${this.lines[i] * zoom}`
            d += path_route;
        }
        return d;
    }

    get_storage(){
        return {id: this.id_name, x: this.ax, y: this.ay, first_target: this.first_target, second_target: this.second_target, lines: this.lines };
    }

    get_rectbox(offset = 10){
        
        this.calc_rectbox()
        return {x: this.x - offset, y: this.y - offset, max_x: (this.max_x + offset*2), max_y: (this.max_y + offset*2)};
    }

    calc_rectbox(){
        let lines_x = [];
        let lines_y = [];
        for (let i = 0; i < this.lines.length; i++){
            if ( (i % 2) == 0 ) {
                lines_x.push(this.lines[i]);
            }
            else { lines_y.push(this.lines[i]); }
        }
        this.x = Math.min(this.ax, ...lines_x);
        this.y = Math.min(this.ay, ...lines_y);
        this.max_x = Math.max(this.ax, ...lines_x);
        this.max_y = Math.max(this.ay, ...lines_y);
    }

    append_line(value){
        this.lines.push(round5(value));
    }

    get_last_line_i() {
        return this.lines.length - 1;
    }

    set_rectbox_x(x) {
        this.x = Math.min(this.x, x);
        this.max_x = Math.max(this.max_x, x);
    }

    set_rectbox_y(y) {
        this.y = Math.min(this.y, y);
        this.max_y = Math.max(this.max_y, y);
    }

    set_lines(lines){
        this.lines = lines;
    }

    set_line(index, value){
        if (typeof(value) === "number"){
            let parameters;
            let editor = GetEditorApp();
            if( (index % 2) == 0){ parameters = {this: this, pos: "x", pos_max: "max_x", value: value, start_pos: "ax", index: index, lines: "lines"}; }
            else { parameters = {this: this, pos: "y", pos_max: "max_y", value: value, start_pos: "ay", index: index, lines: "lines"}; }
            editor.undo.push([_set_line(parameters)])
        }
        return -1;


        // this.method_name || this.value === this["method_name"] || this.["value"]
        // данная функция записывается в стек команд отменяющих действие (undo) пользователя и возвращает команду возврата в исходное состояние (return в redo).
        function _set_line(p){
            if(p.this && p.pos && p.pos_max && p.start_pos && !isNaN(p.index) && p.lines){
                if (typeof(p.value) === "number"){
                    let zoom_value = p.value / get_zoom();
                    p.this[p.pos] = Math.min(p.this[p.pos], zoom_value, p.this[p.start_pos]);
    
                    p.this[p.pos_max] = Math.max(p.this[p.pos_max], zoom_value, p.this[p.start_pos]);
                    let last_value = p.this[p.lines][p.index];
                    p.this[p.lines][p.index] = zoom_value;
                    let res_params = {this: p.this, pos: p.pos, pos_max: p.pos_max, value: last_value, start_pos: p.start_pos, index: p.index, lines: p.lines}
                    return {command: _set_line, parameters: res_params}
                }
            }
        }
    }

    move(x, y, target_name){
        let set_pos = {x: undefined, y: undefined}
        if (target_name == this.first_target.target){
            this.ax += x;
            this.ay += y;
            this.path_start = `m ${this.ax} ${this.ay} `
            set_pos = { x: this.ax, y: this.ay };
        }
        if (target_name == this.second_target.target){
            if ( ((this.lines.length - 1) % 2) == 0 ) {
                this.lines[this.lines.length - 1] += x;
                this.lines[this.lines.length - 2] += y;
                set_pos = {x: this.lines[this.lines.length - 1], y: this.lines[this.lines.length - 2]}
            }
            else {
                this.lines[this.lines.length - 1] += y;
                this.lines[this.lines.length - 2] += x;
                set_pos = {y: this.lines[this.lines.length - 1], x: this.lines[this.lines.length - 2]}
            }
        }
        this.set_rectbox_x(set_pos.x);
        this.set_rectbox_y(set_pos.y);
        document.$("svg#connectorLines").componentUpdate();
    }

    move_first_target(x, y){
        if(!isNaN(x+y)){
            this.ax = x;
            this.ay = y;
            this.path_start = `m ${this.ax} ${this.ay} `
            this.set_rectbox_x(x);
            this.set_rectbox_y(y);
            return true;
        }
        return false;
    }

    move_second_target(x, y){
        if (!isNaN(x + y)){
            if ( ((this.lines.length - 1) % 2) == 0 ) {
                this.lines[this.lines.length - 1] = x;
                this.lines[this.lines.length - 2] = y;
            }
            else {
                this.lines[this.lines.length - 1] = y;
                this.lines[this.lines.length - 2] = x;
            }
            this.set_rectbox_x(x);
            this.set_rectbox_y(y);
            return true;
        }
        return false;
    }

    move_selected(ax, ay, cx, cy){
        if(!isNaN(ax + ay + cx + cy)){
            for (let i = 0; i < this.lines.length - 2; i++ ){
                this.lines[i] += (i % 2 == 0) ? (cx - ax) : (cy - ay);
            }
            this.componentUpdate();
            return true;
        }
        else {
            console.error("Move positions is NaN!");
            return false;
        }
    }

    set_hidden(){
        this.visibility = "hidden";
        this.componentUpdate();
    }

    SetSelect(container){
        let line = container.$(`#${this.id_name}`);
        line.attributes["selected"] = true;
    }

    doDrag_line(element, evt, index, container, svg_connects){
        index -= 1;
        let res = false;
        let editor = GetEditorApp();
        let zoom = get_zoom();
        let path_draw = {start: `m ${(this.ax + editor.left) * zoom} ${(this.ay + editor.top) * zoom} `, 
                        index: "", end: ""}
        
        var cx = roundX(evt.clientX - editor.offsetLeft, 5 * zoom);
        var cy = roundX(evt.clientY - editor.offsetTop, 5 * zoom); 
        
        for( let i = 0; i < container.lines.length; i++) {
            let path_route = (i % 2 == 0) ? ` H ${(container.lines[i] + editor.left) * zoom}` : ` V ${(container.lines[i] + editor.top) * zoom}`
            if (i < index){
                path_draw.start += path_route;
            }
            else if (i > index){
                path_draw.end += path_route;
            }
        }

        element.post(function() {
            element.state.capture(true);
            editor.on("mousemove", drag_onmove);
            svg_connects.on("mouseup", mouseup);
            editor.paintForeground = draw_select_path;
        });

        return res;
        
        function drag_onmove(e) {
            cx = roundX(e.clientX - editor.offsetLeft, 5 * zoom); //Update the current position X
            cy = roundX(e.clientY - editor.offsetTop, 5 * zoom); //Update the current position Y
            res = true;
            editor.requestPaint();
        }

        function mouseup(evt){
            editor.paintForeground = undefined;
            editor.requestPaint();
            element.state.capture(false);
            editor.off(drag_onmove);
            container.set_line(index, ((index % 2) == 0) ? cx - editor.left * zoom : cy - editor.top * zoom);
            svg_connects.componentUpdate();
            
            svg_connects.off(mouseup);
        }
        
        function draw_select_path(gfx){
            let path_changing = (index % 2 == 0) ? ` H ${cx}` : ` V ${cy}`;
            path_draw.index = path_changing;

            gfx.lineWidth = 2;
            gfx.strokeStyle = Color.RGB(148,148,148);
            gfx.fillStyle = Color.RGB(148,148,148, 50);
            let path = new Graphics.Path(`${path_draw.start}${path_draw.index}${path_draw.end}`);
            gfx.draw(path, {x: 0, y:0, stroke: true})
            //gc();
            return true;
        }
    }
        

    set_rects_line(){
        let container = this;
        let editor = GetEditorApp();
        container.rects_path = new Array();
        let rect_sz = 5;
        let lines = container.lines;
        let zoom = Number(get_zoom());

        container.rects_path_start = []
        container.rect_path_end = []

        container.rects_path_start.push({
            x1: Math.min(container.ax * zoom, lines[0] * zoom) - rect_sz + editor.left * zoom, 
            x2: Math.max(container.ax * zoom, lines[0] * zoom) + rect_sz + editor.left * zoom,
            y1: container.ay * zoom - rect_sz + editor.top * zoom,
            y2: container.ay * zoom + rect_sz + editor.top * zoom});

        container.rects_path.push({ 
            x1: lines[0] * zoom - rect_sz + editor.left * zoom, 
            x2: lines[0] * zoom + rect_sz + editor.left * zoom, 
            y1: Math.min(container.ay * zoom, lines[1] * zoom) - rect_sz + editor.top * zoom, 
            y2: Math.max(container.ay * zoom, lines[1] * zoom) + rect_sz + editor.top * zoom});

        for (let i = 2; i < lines.length - 1; i++){
            container.rects_path.push(_set_pos_rect(i))
        }
        container.rect_path_end.push(_set_pos_rect(lines.length - 1))
        //test_rect_lines();

        function _set_pos_rect(i){
            let x, y;
            if((i % 2) == 0) {
                x =  [  Math.round(Number(lines[i - 2]) * zoom) + editor.left * zoom, 
                        Math.round(Number(lines[i]) * zoom) + editor.left * zoom ];
                y =     Math.round(Number(lines[i - 1]) * zoom + editor.top * zoom);

                return {    x1: Math.min(...x) - rect_sz, 
                            y1: y - rect_sz, 
                            x2: Math.max(...x) + rect_sz, 
                            y2: y + rect_sz };
            }
            else {
                x =     Math.round(Number(lines[i - 1]) * zoom + editor.left * zoom);
                y =  [  Math.round(Number(lines[i - 2]) * zoom + editor.top * zoom), 
                        Math.round(Number(lines[i]) * zoom) + editor.top * zoom ];
                return {    x1: x - rect_sz, 
                            y1: Math.min(...y) - rect_sz, 
                            x2: x + rect_sz, 
                            y2: Math.max(...y) + rect_sz }
            }
        }

        function rect_draw(gfx, rects){
            for (let rect of rects){
                gfx.fillStyle = Color.RGB(148,148,148, 50);
                gfx.strokeStyle = Color.RGB(148,148,148);
                gfx.lineWidth = 1;
                gfx.beginPath()
                gfx.rect(rect.x1, rect.y1, rect.x2 - rect.x1, rect.y2 - rect.y1)
                gfx.stroke();
                gfx.closePath();
            }
        }

        function test_rect_lines() {
            if (editor.paintForeground === undefined || editor.paintForeground == null){
                editor.paintForeground = function(gfx){
                    rect_draw(gfx, container.rects_path)
                    rect_draw(gfx, container.rects_path)
                    return true;
                };
                editor.requestPaint();
            }
        }
    }

    GetRectsPath(){
        return this.rects_path//, ...this.rects_path_start, ...this.rect_path_end]
    }

    GetStartEndPath(){
        return [...this.rects_path_start, ...this.rect_path_end]
    }



    Click(container, evt) {
        container.attributes["selected"] = (container.attributes["selected"] === undefined) ? true : undefined;
        return true;
    }

    static EventClick(evt){
        let editor = GetEditorApp()
        editor.EventsManager.pushEvent({ container: this, callback: this.Click, args: evt, flag: editor.evt_flag }); 
    }

    _setImage(d_attrs)
    {
        
        this.d_attrs = d_attrs;
        this.Image = new Graphics.Path(this.d_attrs);
        //gc();
    }

    SetImageData(zoom)
    {
        let d_attrs = this.get_attribute_d(zoom);
        if (this.Image === null || this.d_attrs !== d_attrs)
        {
            this._setImage(d_attrs);
        }
    }

    GetImage(zoom)
    {
        this.SetImageData(zoom);
        return this.Image;
    }

    render(){
        var lines = ""
        for (let i = 0; i < this.lines.length; i++){
            lines += (i % 2) ? `V ${this.lines[i]} ` : `H ${this.lines[i]} `
        }
        return <g id={this.id_name} style={`margin: 5px;visibility: ${this.visibility};`} class="line_path"/* onclick={ConnectorLine.EventClick}*/>
                    <path stroke="#000000" d={this.path_start + lines}
                    style={`fill:none;
                            stroke-width:${0.2}px;
                            stroke-linecap:butt;
                            stroke-linejoin:miter;
                            `}/>
                </g>
    }
}