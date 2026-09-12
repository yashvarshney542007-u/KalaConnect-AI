/* =========================================
   KALA CONNECT AI - FRONTEND API CONFIG
========================================= */

const API_CONFIG = {

  // Backend ready hone tak false rakho
  USE_AI_API: false,

  BASE_URL: "http://127.0.0.1:8000",

  ENDPOINTS: {
    analyzeProduct: "/api/ai/analyze-product/"
  }

};


/* =========================================
   PRODUCT AI ANALYSIS
========================================= */

async function analyzeProductWithAI({
  imageFile,
  audioBlob = null,
  language = null
}) {

  if(!imageFile){
    throw new Error("Product image is required.");
  }


  const formData =
    new FormData();


  formData.append(
    "image",
    imageFile
  );


  if(audioBlob){

    formData.append(
      "audio",
      audioBlob,
      "artisan-voice.webm"
    );

  }


  if(language){

    formData.append(
      "language",
      language
    );

  }


  const response =
    await fetch(
      API_CONFIG.BASE_URL +
      API_CONFIG.ENDPOINTS.analyzeProduct,
      {
        method: "POST",
        body: formData
      }
    );


  const result =
    await response.json();


  if(
    !response.ok ||
    result.success === false
  ){

    throw new Error(
      result?.error?.message ||
      "Product analysis failed."
    );

  }


  return result;

}