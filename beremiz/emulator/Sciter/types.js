
export class Stack extends Array{
    constructor(size){
        super();
        this.size = size - 1;
    }
    push(value){
        if (this.length > this.size){
            super.shift();
        }
        super.push(value)
    }
}