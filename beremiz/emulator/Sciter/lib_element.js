import * as sys from "@sys";

function GetFrameEditor()  { return document.$("frame#editor"); }

function GetFrameEditorApp(FrameEditor) { return FrameEditor.frame?.document.$("#editor_app"); }

export function Library(props){
    let images = new Array();
    for ( let script of sys.fs.$readdir(URL.toPath(`${__DIR__}/editor/elements/`)) ){
        let target_name = script.name.replace(/[\.]/g, " ").split(" ")[0];
        if (props.frame_doc.globalThis[target_name].get_svg)
        {
            images.push(<LibraryImg target_name={target_name} img_svg={props.frame_doc.globalThis[target_name].get_svg(150, 90, "element")}/>)
        }
        else{
        }
    }
    return <div id="library">
                <p @ >Library: </p>
                    <div id="library_elements">
                        {images}
                    </div>
            </div>
}

class LibraryImg extends Element{
    constructor(props, kids){
        super();
        this.target_name = props.target_name;
        this.img_svg = props.img_svg;
    }

    doDrag(element, evt){
        let lasttarget = null;
        let cx, cy;
      
        function onmove(evt) { 
            //gc();
            lasttarget = evt.target;
            cx = evt.clientX;
            cy = evt.clientY; 
        }
      
        document.post(function() { 
          // 1. setup cursor by rendering element into bitmap and making cursor from that bitmap
          let image = new Graphics.Image(element.$(".element"));
          document.style.setCursor(image, this.offsetLeft, this.offsetLeft);//, x - this.offsetLeft, y - this.offsetTop);
      
          // 2. hide the element itself
          //element.style.visibility = "hidden";
          
          // 3. short circuit mouse moves to document 
          document.state.capture(true);
          document.attributes["dnd"] = "";
          document.on("mousemove",onmove);
      
          // 4. run "mouse modal loop" until mouse depressed
          let r = Window.this.doEvent("untilMouseUp");
          // 5. return things back
          document.state.capture(false);
          document.off(onmove);
          document.style.setCursor(null);
          //element.style.visibility = undefined;
          document.attributes["dnd"] = undefined;
          if (lasttarget.getAttribute("id") === "editor_app"){
            if(!lasttarget.read_only){
                lasttarget.AppendKidFromLib(element.target_name, cx, cy);
            }
          }
          else
          {
            let editor = lasttarget.closest("#editor_app");
            if(editor)
            {
                if(!editor.read_only){
                    editor.AppendKidFromLib(element.target_name, cx, cy);
                }
            }
          }
        });
    }

    onmousedragrequest(evt){
        //
        let editor = GetFrameEditorApp(GetFrameEditor());
        editor.disableEvents();
        this.doDrag(this, evt);
        editor.enableEvents();
    }

    render(){
        return  <div class="element"> <p>{this.target_name}</p>
                    {this.img_svg}
                </div>;
    }
}