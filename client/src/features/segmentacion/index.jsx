import React from 'react'
import { useState } from 'react'
import { segmentacion } from '@/features/segmentacion/apis/segmentacion'
import { useForm } from 'react-hook-form'
import { PacmanLoader } from 'react-spinners'
export default function Segmentacion() {
    const [data, setData] = useState()
    const { register, handleSubmit } = useForm()
    const [expandida, setExpandida] = useState(false)
    const [imagenSeleccionada, setImagenSeleccionada] = useState(null)
    const [loading, setLoading] = useState(false)

    const onSubmit = async (data) => {
        setLoading(true)
        const formData = new FormData();
        formData.append('image', data.file[0]);
        const res = await segmentacion.postSegementacion(formData);
        setData(res);
        console.log(res);
        await new Promise((resolve) => setTimeout(resolve, 2000));
        setLoading(false)
    }
    if (loading) {
        return <div className='flex items-center justify-center min-h-screen'><PacmanLoader color='#3b82f6' size={50} /></div>
    }
    return (
        <>
            <div>Segmentacion de Imagenes</div>
            <br></br>


            <form onSubmit={handleSubmit(onSubmit)} className='flex flex-col gap-2 md:flex-row'>
                <input type='file' {...register('file')} className='bg-white p-1 border-2 rounded-2xl cursor-pointer' />
                <button type='submit' className='bg-blue-400 text-black p-1 border-2 rounded-2xl cursor-pointer' disabled={loading}>
                    {loading ? 'Enviando...' : 'Enviar'}
                </button>
            </form>

            <div className='grid grid-cols-1 md:gap-3 md:grid-cols-3'>
                {data && (
                    data.map((item, index) => (
                        <>
                            <div className="mt-4" style={{ position: "relative", display: "inline-block" }}>
                                <p>Imagen {item.result} {index + 1}:</p>
                                <img src={item.url} alt="Segmentación" className=" border-2" />
                                {/* Botón encima de la imagen */}
                                <button
                                    onClick={() => { setExpandida(true), setImagenSeleccionada(item) }}
                                    className=' text-white  rounded-2xl cursor-pointer absolute top-7 right-2'

                                >
                                    ⛶
                                </button>
                            </div>

                            {expandida &&
                                <ImagenExpanded data={imagenSeleccionada} setExpandida={setExpandida} />

                            }

                        </>


                    ))
                )}
            </div>

        </>

    )
}

function ImagenExpanded({ data, setExpandida }) {
    return (
        <div
            className='fixed inset-0 flex items-center justify-center'
            style={{
                zIndex: 9999,
                backdropFilter: "blur(10px)",
            }}
            onClick={() => setExpandida(false)}
        >
            <div
                className='relative max-w-[90vw] max-h-[90vh] flex flex-col items-center'
                onClick={(e) => e.stopPropagation()}
            >
                <img
                    src={data.url}
                    alt="imagen"
                    className='rounded-lg shadow-2xl'
                    style={{
                        maxWidth: "100%",
                        maxHeight: "85vh",
                        objectFit: "contain"
                    }}
                />

                {/* Botón cerrar más visible */}
                <button
                    onClick={() => setExpandida(false)}
                    className='absolute -top-10 right-0 text-white text-3xl cursor-pointer hover:text-red-400 transitions'
                >
                    ✕
                </button>
                <p className='text-white mt-2 text-xl font-bold'>Imagen {data.result}</p>
            </div>
        </div>
    )
}
