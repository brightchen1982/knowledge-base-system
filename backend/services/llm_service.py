import os
import logging
import yaml
import httpx
from typing import Dict, List, Optional, Any
import json

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, config_path: str = "configs/ollama.yaml"):
        # 加载配置
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        self.host = self.config["ollama"]["host"]
        self.port = self.config["ollama"]["port"]
        self.timeout = self.config["ollama"]["timeout"]
        self.base_url = f"http://{self.host}:{self.port}"
        self.default_model = self.config["models"]["default"]
        self.embeddings_model = self.config["models"]["embeddings"]
        
        # 初始化客户端
        self.client = httpx.Client(timeout=self.timeout)
        
        # 加载推理参数
        self.inference_params = self.config["inference"]
        
        logger.info(f"LLM服务初始化完成，使用模型: {self.default_model}")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """生成LLM响应"""
        model = kwargs.pop("model", self.default_model)
        
        # 准备请求数据
        request_data = {
            "model": model,
            "prompt": prompt,
            **self.inference_params,
            **kwargs
        }
        
        if system_prompt:
            request_data["system"] = system_prompt
        
        try:
            # 请求Ollama API
            response = self.client.post(
                f"{self.base_url}/api/generate",
                json=request_data
            )
            response.raise_for_status()
            
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Ollama API调用失败: {str(e)}")
            raise Exception(f"生成响应失败: {str(e)}")
    
    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None, **kwargs):
        """生成流式LLM响应"""
        model = kwargs.pop("model", self.default_model)
        
        # 准备请求数据
        request_data = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            **self.inference_params,
            **kwargs
        }
        
        if system_prompt:
            request_data["system"] = system_prompt
        
        try:
            with httpx.stream("POST", f"{self.base_url}/api/generate", 
                             json=request_data, timeout=self.timeout) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            if "response" in chunk:
                                yield chunk["response"]
                        except json.JSONDecodeError:
                            logger.warning(f"无法解析JSON响应: {line}")
        except httpx.HTTPError as e:
            logger.error(f"Ollama流式API调用失败: {str(e)}")
            raise Exception(f"生成流式响应失败: {str(e)}")
    
    def get_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        """获取文本的向量嵌入"""
        model = model or self.embeddings_model
        
        try:
            response = self.client.post(
                f"{self.base_url}/api/embeddings",
                json={"model": model, "prompt": text}
            )
            response.raise_for_status()
            result = response.json()
            
            return result["embedding"]
        except httpx.HTTPError as e:
            logger.error(f"获取向量嵌入失败: {str(e)}")
            raise Exception(f"生成向量嵌入失败: {str(e)}") 
