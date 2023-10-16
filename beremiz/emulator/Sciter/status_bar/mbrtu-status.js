
export class MbrtuStatus extends Element{
  STARTED = @"Started"
  STOPPED = @"Stopped"
  ON = @"on"
  SERVER_MBRTU = @"Server MBRTU"
  constructor()
  {
    super();
    this.com_port = "";
    this.status = false;
    this.mode = "Slave"
    this._editor_is_load = false;
    globalThis["MbrtuStatusClass"] = this;
  }

  setEditorFlag(flag)
  {
    this._editor_is_load = flag;
  }
  
  setComPort(com_port)
  {
    if (typeof com_port == "string")
    {
      this.com_port = com_port;
    }
  }
  /**
   * 
   * @param status - number mode
   *  @args
   *      false - stopped
   *      true - started
   */
  setStatus(status)
  {
    console.log("SetStatus mbrtu");
    if(typeof status == "boolean")
    {
      console.log("status is bool");
      this.status = status;
      this.componentUpdate();
    }
  }
  setMode(mode)
  {
    if (typeof mode == "string")
    {
      this.mode = mode;
    }
  }

  editorIsLoad()
  {
    return this._editor_is_load;
  }

  SetData(com_port, mode)//this.attrs["COM port"], this.attrs["Mode"])
  {
    console.log("SetData");
    this.setComPort(com_port);
    this.setMode(mode);
    this.componentUpdate();
  }


  render(){
    let status = (this.status) ? this.STARTED : this.STOPPED ;

    let message;
    if (this.editorIsLoad() && this.com_port.length > 0)
    {
      message = `${this.SERVER_MBRTU} ${this.mode} ${this.ON} ${this.com_port}  |    ${status}`
    }
    else 
    {
      message = `${this.SERVER_MBRTU}  |    ${status}`
    }
    return  <div> {message} </div>
  }
}

