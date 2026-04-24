import React, { useState } from 'react';
import { Handle, Position } from '@xyflow/react';
import { Upload, Maximize2, Trash2, ImageIcon } from 'lucide-react';

export default function ImageNode({ data }) {
    const [preview, setPreview] = useState(null);

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            const url = URL.createObjectURL(file);
            setPreview(url);
            data.onImageSelect(file);
        }
    };

    const removeImage = () => {
        setPreview(null);
        data.onImageSelect(null);
    };

    return (
        <div className="bg-slate-900 border-2 border-blue-500 rounded-2xl p-4 shadow-2xl min-w-[220px]">
            <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-2">
                <div className="flex items-center gap-2">
                    <ImageIcon size={16} className="text-blue-400" />
                    <span className="text-[10px] font-black uppercase text-slate-300 tracking-tighter">{data.label}</span>
                </div>
                <div className="flex gap-1">
                    {preview && (
                        <button 
                            onClick={() => data.onExpand(preview)} // Llama al modal
                            className="text-slate-500 hover:text-white transition-colors"
                        >
                            <Maximize2 size={14} />
                        </button>
                    )}
                </div>
            </div>

            <div className="relative group">
                {!preview ? (
                    <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-slate-700 rounded-xl cursor-pointer hover:border-blue-500 hover:bg-blue-500/5 transition-all">
                        <Upload className="text-slate-500 mb-2" size={24} />
                        <span className="text-[9px] text-slate-500 font-bold uppercase">Subir MRI</span>
                        <input type="file" className="hidden" accept="image/*" onChange={handleFileChange} />
                    </label>
                ) : (
                    <div className="relative overflow-hidden rounded-xl">
                        <img src={preview} className="w-full h-32 object-cover border border-slate-700" alt="Preview" />
                        <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-4">
                            <button onClick={removeImage} className="bg-red-500 p-2 rounded-full hover:scale-110 transition-transform shadow-lg">
                                <Trash2 size={16} />
                            </button>
                        </div>
                    </div>
                )}
            </div>

            {/* Handle de salida HACIA ABAJO */}
            <Handle
                type="source"
                position={Position.Bottom}
                className="w-3 h-3 bg-blue-400 border-2 border-slate-900 !-bottom-1.5"
            />
        </div>
    );
}
