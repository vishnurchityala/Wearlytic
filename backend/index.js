const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');
require('dotenv').config();

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB Connection
mongoose.connect(process.env.MONGODB_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
    serverSelectionTimeoutMS: 5000,
    socketTimeoutMS: 45000,
    connectTimeoutMS: 10000,
    maxPoolSize: 50,
    minPoolSize: 10
})
.then(() => console.log('Connected to MongoDB'))
.catch(err => console.error('MongoDB connection error:', err));

// Product Schema
const productSchema = new mongoose.Schema({
    description: String,
    product_url: String,
    source: String,
    product_name: String,
    image_url: String,
    category: String,
    price: String,
    colors: [String],
    brand: String,
    material: String,
    timestamp: Number
});

const Product = mongoose.model('Product', productSchema);

// Helper function to build pagination links
const buildPaginationLinks = (req, page, totalPages, query) => {
    const baseUrl = `${req.protocol}://${req.get('host')}${req.path}`;
    const queryParams = new URLSearchParams(query);
    
    const buildUrl = (pageNum) => {
        queryParams.set('page', pageNum);
        return `${baseUrl}?${queryParams.toString()}`;
    };

    return {
        first: buildUrl(1),
        last: buildUrl(totalPages),
        prev: page > 1 ? buildUrl(page - 1) : null,
        next: page < totalPages ? buildUrl(page + 1) : null,
        self: buildUrl(page)
    };
};

// Routes
app.get('/api/products', async (req, res) => {
    try {
        const startTime = Date.now();
        
        // Get query parameters
        const { 
            search = '', 
            category = '', 
            brand = '', 
            min_price = '', 
            max_price = '', 
            page = 1, 
            per_page = 5 
        } = req.query;

        const currentPage = parseInt(page);
        const itemsPerPage = parseInt(per_page);

        // Build query
        const query = {};
        
        // Search in description and brand
        if (search) {
            query.$or = [
                { description: { $regex: search, $options: 'i' } },
                { brand: { $regex: search, $options: 'i' } }
            ];
        }

        // Add category filter
        if (category) {
            query.category = { $regex: category, $options: 'i' };
        }

        // Add brand filter
        if (brand) {
            query.brand = { $regex: brand, $options: 'i' };
        }

        // Add price range filter
        if (min_price || max_price) {
            const priceQuery = {};
            if (min_price) {
                const minPriceFloat = parseFloat(min_price.replace('₹', '').trim());
                priceQuery.$gte = minPriceFloat;
            }
            if (max_price) {
                const maxPriceFloat = parseFloat(max_price.replace('₹', '').trim());
                priceQuery.$lte = maxPriceFloat;
            }
            if (Object.keys(priceQuery).length > 0) {
                query.price = priceQuery;
            }
        }

        // Get total count
        const totalProducts = await Product.countDocuments(query);
        const totalPages = Math.ceil(totalProducts / itemsPerPage);

        // Get paginated results
        const skip = (currentPage - 1) * itemsPerPage;
        const products = await Product.find(query)
            .select('-_id description product_url source product_name image_url category price colors brand material timestamp')
            .skip(skip)
            .limit(itemsPerPage);

        const executionTime = Date.now() - startTime;
        console.log(`Query executed in ${executionTime}ms`);

        // Build pagination links
        const links = buildPaginationLinks(req, currentPage, totalPages, {
            search,
            category,
            brand,
            min_price,
            max_price,
            per_page: itemsPerPage
        });

        res.json({
            products,
            pagination: {
                total: totalProducts,
                page: currentPage,
                per_page: itemsPerPage,
                total_pages: totalPages,
                links
            }
        });
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ error: error.message });
    }
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'ok' });
});

// Start server with port fallback and error handling
const startServer = async () => {
    const port = process.env.PORT || 3001;
    try {
        await app.listen(port);
        console.log(`Server is running on port ${port}`);
    } catch (error) {
        if (error.code === 'EADDRINUSE') {
            console.log(`Port ${port} is busy, trying port ${port + 1}`);
            await app.listen(port + 1);
            console.log(`Server is running on port ${port + 1}`);
        } else {
            console.error('Failed to start server:', error);
            process.exit(1);
        }
    }
};

startServer();

module.exports = app; 