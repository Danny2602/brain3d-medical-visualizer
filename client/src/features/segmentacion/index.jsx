import React from 'react'
import { useState } from 'react'
import { segmentacion } from '@/features/segmentacion/apis/segmentacion'
import { useForm } from 'react-hook-form'
export default function Segmentacion() {
    const [data, setData] = useState()
    const { register, handleSubmit } = useForm()

    // const postData = async (numero) => {
    //     const val = await segmentacion.postSegementacion(numero)
    //     console.log(val)
    //     setData(val.result)
    // }

    const onSubmit = async (data) => {
        const formData = new FormData();
        formData.append('image', data.file[0]);
        const res = await segmentacion.postSegementacion(formData);
        setData(res);
        console.log(res);
    }

    return (
        <>
            <div>Segmentacion de Imagenes</div>
            <br></br>


            <form onSubmit={handleSubmit(onSubmit)} className='flex gap-2'>
                <input type='file' {...register('file')} className='bg-white p-1 border-2 rounded-2xl cursor-pointer' />
                <button type='submit' className='bg-blue-400 text-black p-1 border-2 rounded-2xl cursor-pointer'>Enviar</button>
            </form>

            <div className='grid grid-cols-2 gap-2'>
                {data && (
                    data.map((item, index) => (
                        <div className="mt-4">
                            <p>Imagen {item.result} {index + 1}:</p>
                            <img src={item.url} alt="Segmentación" className="max-w-md border-2" />
                        </div>
                    ))
                )}
            </div>

        </>

    )
}
