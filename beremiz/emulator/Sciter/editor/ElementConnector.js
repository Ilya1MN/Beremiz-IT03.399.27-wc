import { ConnectorLine } from "./connectorLine";
import { get_zoom } from "./editor";
import { _get_pos_connector } from "./sim_elem"


function GetEditorApp() { return document.$("#editor_app"); }

export class ElementConnector extends Element {
  constructor(props, kids, parent) {
      super();
      this.index        = props.index;
      this.id_name      = props.id_name;
      this.wh           = (props.wh) ? props.wh : 8;
      this.x            = props.x - this.wh / 2;
      this.y            = props.y - this.wh / 2;
      this.target       = props.target;
      this.line_path    = new Array();
      this.element      = props.element;
      this.direction    = props.interface;
      this.interface = undefined;
      this.interface_name = props.interface_name;
      this.connector_value = 0;

      if (this.direction === "input"){
          if (this.element){
              this.interface = (set_value)=>{ this.element.input_set(this.interface_name, this.index, set_value) }
          }
          else{
              this.interface = (set_value)=>{};
          }
      }
  }

  get_callback(){
      if (this.interface){
          return this.interface
      }
  }

  set_callback(callback){
      this.interface = callback
  }

  set_out_last_value(){ 
        this.set_out(this.connector_value)
    }


  set_out(set_value){
      if(this.interface){
        this.interface(set_value);
        this.connector_value = set_value;
      }
  }

  clear_output_interface(){
      if(this.direction === "output"){
          if(this.interface){
              this.interface = undefined;
          }
      }
  }

  get_lines_path() {
      return this.line_path;
  }

  SetConnector(element, evt, ax, ay, connector) {
      var editor = GetEditorApp();
      var click_count = 0;
      var click_count_old = 0;
      let zoom = get_zoom();
      var path_str = `m ${(ax + editor.left) * zoom} ${(ay + editor.top) * zoom}`; 
      var cx, cy;
      var _mousemove = false;
      

      element.post(function(){
          editor.state.capture(true);
          editor.addEventListener("mousemove", onmove);
          editor.addEventListener("click", function(e){ 
              if (click_count != 0){
                  ax = e.clientX - editor.offsetLeft;
                  ay = e.clientY - editor.offsetTop;
              }
              click_count++;
              })
          })

      function onmove(e) {
          cx = e.clientX - editor.offsetLeft;
          cy = e.clientY - editor.offsetTop;
          if (!_mousemove && (editor.paintForeground !== drawConnector)){
              editor.paintForeground = drawConnector;
              _mousemove = true;
          }
      }

      function drawConnector(gfx) {
          let x = cx;
          let y = cy;
          gfx.lineWidth = 2;
          let path_draw;
          gfx.strokeStyle = Color.RGB(148,148,148);
          gfx.fillStyle = Color.RGB(148,148,148, 50);
          
          if ((click_count % 2) == 0) {
              path_draw = ` H ${x} V ${y}`;
              if (click_count != click_count_old){
                  path_str += ` V ${y}`;
                  connector.append_line((y / zoom - editor.top));
                  click_count_old = click_count;
              }
          }
          else {
              path_draw = ` V ${y} H ${x}`;
              if (click_count != click_count_old){
                  connector.append_line((x / zoom - editor.left));
                  path_str += ` H ${x}`;
                  click_count_old = click_count;
              }
          }
              
          let path = new Graphics.Path(path_str + path_draw);
          gfx.draw(path, {x: 0, y:0, stroke: true})
          editor.requestPaint();
          //gc();
          return true;
      }
  }

  render() {
      return <div id={this.id_name} class="connector"
                  style={`left: ${this.x};
                          top: ${this.y};
                          width: ${this.wh};
                          height: ${this.wh};`}>
              </div>;
  }

  ["on mouseover at div.connector"](evt) {
      let editor = GetEditorApp();
      if(!editor.read_only)
      {
          evt.target.style.backgroundColor = "red";
          /*evt.target.style.border = "0.1px solid";*/
      }
  }
  isConnected()
  {
  }

  EventClickConnector(container, evt)
  {
    var element = container.closest(".draggable");
    var editor = GetEditorApp();
    //let zoom = get_zoom();
    const svg_conn = editor.get_connectors();
    if(!editor.read_only && !svg_conn.isConnected(element.get_target(), container.id_name)) 
    {
      //var offset = {top: editor.offsetTop, left: editor.offsetLeft}
      //var [x,y,width, height] = container.state.box("xywh", "border", "document");

      if (!editor.dragg){
        editor.dragg = true;
        /*var ax = ((x + width/2) - (offset.left));
        var ay = ((y + height/2) - (offset.top));*/
        let index = svg_conn.lines.length;
        let [ax, ay] = _get_pos_connector(container, element.left + 5, element.top + 5);
        editor.connector = new ConnectorLine({id: index, x: ax, y: ay, target: element.get_target(), channel: container.id_name, first_direction: container.direction});
        editor.keys_event.add_event("Escape", key_down)
        function key_down(){
          editor.connector = undefined
          editor.removeEventListener("mousemove");
          editor.removeEventListener("click");
          editor.paintForeground = undefined;
          editor.dragg = false;
          editor.requestPaint()
          editor.keys_event.remove_event()
        }
        return container.SetConnector(container, evt, ax, ay, editor.connector);
      }
      else {
        let connector = editor.connector;
        if (element.get_target() != connector.first_target.target || 
                container.id_name != connector.first_target.ch) {
          editor.dragg = false;
          //var end_x = ((x + width/2) - offset.left) - editor.left * zoom;
          //var end_y = ((y + height/2)- offset.top) - editor.top * zoom;
          let [end_x, end_y] = _get_pos_connector(container, element.left + 5, element.top + 5);
          
          let [first_pos, second_pos] = ( connector.get_last_line_i() % 2 ) ? [end_x, end_y] : [end_y, end_x];

          connector.append_line(first_pos);
          connector.append_line(second_pos);

          connector.set_second_target(element.get_target(), container.id_name, container.direction)
          svg_conn.append_connector(connector);

          editor.paintForeground = undefined;
          svg_conn.componentUpdate();
          editor.keys_event.remove_event()
          editor.removeEventListener("mousemove");
          editor.removeEventListener("click");
          return true;
        }
      }
    }
  }

  ["on click at div.connector"](evt) 
  {
    var editor = GetEditorApp();
    editor.EventsManager.pushEvent( {container: this, callback: this.EventClickConnector, args: evt, flag: editor.evt_flag}); 
  }
  

  ["on mouseout at div.connector"](evt) {
    var editor = GetEditorApp();
    if(!editor.read_only) {
        evt.target.style.backgroundColor = undefined;
    }
  }
}