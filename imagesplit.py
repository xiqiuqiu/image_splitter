import streamlit as st
from PIL import Image
import io
import zipfile
import base64
import os

# 页面配置
st.set_page_config(
    page_title="图片切分工具",
    page_icon="✂️",
    layout="wide"
)

# 添加自定义CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton > button {
        width: 100%;
    }
    .download-btn {
        margin-top: 1rem;
    }
    .result-image {
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 5px;
    }
    .success {
        color: #27ae60;
        font-weight: bold;
    }
    .error {
        color: #e74c3c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 设置标题和简介
st.title('✂️ 图片切分工具')
st.markdown('上传一张图片，选择切分方向和数量，然后下载切分后的图片。')

# 初始化会话状态
if 'split_images' not in st.session_state:
    st.session_state.split_images = []
if 'original_image' not in st.session_state:
    st.session_state.original_image = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = ""

# 创建两列布局
col1, col2 = st.columns([1, 2])

# 左侧控制栏
with col1:
    st.subheader('设置')
    
    # 文件上传部分
    uploaded_file = st.file_uploader("上传图片", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file is not None:
        try:
            # 保存原始文件名
            st.session_state.file_name = uploaded_file.name
            
            # 加载图片
            image = Image.open(uploaded_file)
            st.session_state.original_image = image
            
            # 显示图片信息
            st.info(f"图片尺寸: {image.width} x {image.height} 像素")
            
            # 切分选项
            st.subheader('切分选项')
            
            # 切分方向
            direction = st.radio(
                "切分方向",
                ["横向切分", "竖向切分"],
                horizontal=True
            )
            
            # 切分数量
            # 最大切分数量需要根据用户输入决定
            max_slices = st.number_input("最大切分数量", min_value=2, max_value=100,value=10)
            if direction == "横向切分":
                max_value = min(image.height, max_slices)
            else:
                max_value = min(image.width, max_slices)
            
            count = max_slices
            
            # 切分按钮
            if st.button("开始切分"):
                with st.spinner('正在处理中...'):
                    try:
                        # 重置之前的切分结果
                        st.session_state.split_images = []
                        
                        # 获取图片尺寸
                        img_width, img_height = image.size
                        
                        # 根据方向计算每块的尺寸
                        if direction == "横向切分":
                            slice_height = img_height // count
                            extra_pixels = img_height % count
                            
                            # 切分图片
                            for i in range(count):
                                # 计算当前切片的高度（最后一个切片可能略大）
                                current_height = slice_height
                                if i == count - 1:
                                    current_height += extra_pixels
                                
                                # 计算起始位置
                                start_y = i * slice_height
                                
                                # 切分图片
                                img_slice = image.crop((0, start_y, img_width, start_y + current_height))
                                
                                # 保存切片
                                img_byte_arr = io.BytesIO()
                                img_slice.save(img_byte_arr, format=image.format or 'PNG')
                                img_byte_arr.seek(0)
                                
                                st.session_state.split_images.append({
                                    'image': img_slice,
                                    'bytes': img_byte_arr,
                                    'name': f"split_{i+1}.{image.format.lower() if image.format else 'png'}"
                                })
                        else:  # 竖向切分
                            slice_width = img_width // count
                            extra_pixels = img_width % count
                            
                            # 切分图片
                            for i in range(count):
                                # 计算当前切片的宽度（最后一个切片可能略大）
                                current_width = slice_width
                                if i == count - 1:
                                    current_width += extra_pixels
                                
                                # 计算起始位置
                                start_x = i * slice_width
                                
                                # 切分图片
                                img_slice = image.crop((start_x, 0, start_x + current_width, img_height))
                                
                                # 保存切片
                                img_byte_arr = io.BytesIO()
                                img_slice.save(img_byte_arr, format=image.format or 'PNG')
                                img_byte_arr.seek(0)
                                
                                st.session_state.split_images.append({
                                    'image': img_slice,
                                    'bytes': img_byte_arr,
                                    'name': f"split_{i+1}.{image.format.lower() if image.format else 'png'}"
                                })
                        
                        # 显示成功消息
                        st.success(f"切分完成！共生成 {len(st.session_state.split_images)} 张图片")
                    except Exception as e:
                        st.error(f"切分失败: {str(e)}")
        except Exception as e:
            st.error(f"加载图片失败: {str(e)}")
    
    # 如果有切分结果，显示下载按钮
    if st.session_state.split_images:
        st.subheader("下载")
        
        if len(st.session_state.split_images) == 1:
            # 单个图片下载
            img_data = st.session_state.split_images[0]['bytes'].getvalue()
            filename = st.session_state.split_images[0]['name']
            
            st.download_button(
                label="下载切分图片",
                data=img_data,
                file_name=filename,
                mime=f"image/{filename.split('.')[-1]}"
            )
        else:
            # 多个图片打包下载
            # 创建一个ZIP文件
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for idx, img_data in enumerate(st.session_state.split_images):
                    zip_file.writestr(img_data['name'], img_data['bytes'].getvalue())
            
            # 提供下载按钮
            base_name = os.path.splitext(st.session_state.file_name)[0]
            st.download_button(
                label="下载所有切分图片 (ZIP)",
                data=zip_buffer.getvalue(),
                file_name=f"{base_name}_splits.zip",
                mime="application/zip"
            )

# 右侧预览区
with col2:
        # 使用占位符调整图片位置
    placeholder = st.empty()
    # 原始图片预览
    if st.session_state.original_image is not None:
        st.subheader("原始图片")
        st.image(st.session_state.original_image, width=500)
    
    # 切分结果预览
    if st.session_state.split_images:
        st.subheader("切分结果")
        
        # 创建一个多列布局来显示切分结果
        columns_per_row = 3  # 每行显示3张图片
        rows = (len(st.session_state.split_images) + columns_per_row - 1) // columns_per_row
        
        for r in range(rows):
            row_cols = st.columns(columns_per_row)
            for c in range(columns_per_row):
                idx = r * columns_per_row + c
                if idx < len(st.session_state.split_images):
                    with row_cols[c]:
                        st.image(
                            st.session_state.split_images[idx]['image'], 
                            caption=f"切片 {idx+1}",
                            use_container_width =True
                        )
                        # 单独下载此图片的按钮
                        img_data = st.session_state.split_images[idx]['bytes'].getvalue()
                        filename = st.session_state.split_images[idx]['name']
                        st.download_button(
                            label=f"下载此切片",
                            data=img_data,
                            file_name=filename,
                            mime=f"image/{filename.split('.')[-1]}",
                            key=f"download_{idx}"
                        )

# 页脚
st.markdown("---")
st.markdown("图片切分工具 | 使用Streamlit构建:balloon:")
